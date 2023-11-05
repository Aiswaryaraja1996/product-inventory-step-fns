import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
stepFunction = boto3.client("stepfunctions")
productTable = dynamodb.Table("Products")
userTable = dynamodb.Table("Users")


class ProductNotFoundError(Exception):
    pass


class ProductOutOfStockError(Exception):
    pass


class CouponNotRedeemedError(Exception):
    pass


class NoSufficientMoneyError(Exception):
    pass


def checkInventoryFn(event, context):
    productId = event["productId"]
    orderedQty = event["productQty"]
    productInfo = productTable.get_item(Key={"productId": str(productId)})
    if "Item" not in productInfo:
        raise ProductNotFoundError("Product Not Found")
    else:
        availableQty = productInfo["Item"]["productQty"]
        if orderedQty > availableQty:
            raise ProductOutOfStockError("Product Out Of Stock")
        else:
            return productInfo["Item"]


def calculateProductTotalFn(event, context):
    price = event["productInfo"]["productPrice"]
    qty = event["productQty"]
    total = price * qty
    return {"total": total}


def deductCouponFn(userId):
    userTable.update_item(
        Key={"userId": str(userId)},
        UpdateExpression="SET coupon = :n",
        ExpressionAttributeValues={
            ":n": 0,
        },
    )


def redeemCouponFn(event, context):
    userId = event["userId"]
    userInfo = userTable.get_item(Key={"userId": str(userId)})
    coupon = userInfo["Item"]["coupon"]
    total = event["billInfo"]["total"]
    deposit = userInfo["Item"]["userDeposit"]
    if total < coupon:
        raise CouponNotRedeemedError("Coupon cannot be redeemed!")
    else:
        deductCouponFn(userId)
        orderTotal = total - coupon
        return {"mrp": total, "sp": orderTotal, "coupon": coupon, "deposit": deposit}


def debitDepositAmountFn(userId, sp):
    userTable.update_item(
        Key={"userId": str(userId)},
        UpdateExpression="SET userDeposit = userDeposit - :n",
        ExpressionAttributeValues={
            ":n": sp,
        },
    )


def billProductFn(event, context):
    deposit = event["billInfo"]["deposit"]
    sp = event["billInfo"]["sp"]
    userId = event["userId"]
    if sp > deposit:
        raise NoSufficientMoneyError("No enough money in account to place your order!")
    else:
        debitDepositAmountFn(userId, sp)
        balance = deposit - sp
        return {"msg": "Billing successful!", "balance": balance}


def restoreCouponFn(event, context):
    userId = event["userId"]
    coupon = event["billInfo"]["coupon"]
    userTable.update_item(
        Key={"userId": str(userId)},
        UpdateExpression="SET coupon = :n + coupon",
        ExpressionAttributeValues={
            ":n": coupon,
        },
    )


def restoreDepositFn(event, context):
    userId = event["userId"]
    sp = event["billInfo"]["sp"]
    userTable.update_item(
        Key={"userId": str(userId)},
        UpdateExpression="SET userDeposit = userDeposit + :n",
        ExpressionAttributeValues={
            ":n": sp,
        },
    )


def updateProductQtyFn(productId, productQty):
    productTable.update_item(
        Key={"productId": str(productId)},
        UpdateExpression="SET productQty = productQty - :n",
        ExpressionAttributeValues={
            ":n": productQty,
        },
    )


def restoreProductQtyFn(event, context):
    productQty = event["productQty"]
    productId = event["productId"]
    productTable.update_item(
        Key={"productId": str(productId)},
        UpdateExpression="SET productQty = productQty + :n",
        ExpressionAttributeValues={
            ":n": productQty,
        },
    )


# this lambda function consumes the message in the queue pushed by the step function task
def sqsWorkerFn(event, context):
    body = json.loads(event["Records"][0]["body"])  # converts string to json
    updateProductQtyFn(body["Input"]["productId"], body["Input"]["productQty"])
    courier = "courier mail address"
    try:
        stepFunction.send_task_success(
            taskToken=body["Token"], output=json.dumps({"courier": courier})
        )
    except Exception as e:
        logger.info(e)
        stepFunction.send_task_failure(
            taskToken=body["Token"],
            cause="Courier Service not available!",
            error="NoCourierServiceAvailable",
        )

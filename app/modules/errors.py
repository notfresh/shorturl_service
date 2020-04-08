# -*- coding:utf-8 -*-


ERRORS = {
    'APITimingError': [60001, 'API调用时序错误'],
    'FieldIncomplete': [60002, '字段缺失错误'],
    'APICallError': [60003, 'API调用错误，该用户不应该调用该API'],
    'OrderUnPaid': [60004, '订单尚未支付'],
    'SmsCodeError': [60005, '短信验证码错误'],
    'DataRelationError': [60006, '数据归属错误'],
    'UserAuthError': [60007, '用户账号或密码为空'],
    'DataNotFound': [60008, '数据不存在'],
    'MethodNotSupport': [60009, '不支持该方法'],
    'DuplicateError': [60010, '数据不允许重复'],
    'DataNotAllowed': [60011, '数据不被允许'],
    'FakeDataError': [60012, '数据造假'],
    'EventError': [60013, '活动相关错误'],
    'TicketTypeError': [60014, '票种相关错误'],
    'WithdrawNotHandle': [60015, '有未处理的提现申请'],
    'WithdrawAmountError': [60016, '提现金额与账户可提现金额不符'],
    'AuditHandled': [60017, '该条审核申请已经处理过']
}

MISS_DATA = {
    "msg": "数据不存在"
}

SUCCESS = {"msg": "操作成功"}
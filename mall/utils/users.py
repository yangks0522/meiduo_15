def jwt_response_payload_handler(token, user=None, request=None):
    return {
        # jwt 的token
        # user  就是已经认证之后的用户信息
        'token': token,
        'user': user.username,
        'user_id': user.id
    }
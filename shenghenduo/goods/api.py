



# 用于存储用户信息的字典
users_db = {}

@app.post("/users/")
async def create_user(user: User):
    users_db[user.id] = user
    return {"message": `User created successfully`, "user": user}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = users_db.get(user_id)
    if user:
        return user
    return {"error": `User not found`}






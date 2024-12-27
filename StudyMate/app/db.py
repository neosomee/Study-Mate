import aiosqlite
from app.classes import User, AddTask


class Database:
    def __init__(self, path):
        self.path = path

    # create tables
    async def create_users_table(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY NOT NULL,
                fullname TEXT,
                age INTEGER,
                number TEXT
            );''')
            await db.commit()

    async def get_user(self, user_id):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"SELECT * FROM users WHERE id = {user_id}") as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return
                user = User()
                user.id = int(row[0])
                user.fullname = row[1]
                user.age = int(row[2])
                user.number = row[3]
                return user

    async def del_user(self, user_id):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"DELETE FROM users WHERE id = {user_id}")
            await db.commit()

    async def save_user(self, user: User):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO users (id, fullname, age, number) VALUES (?, ?, ?, ?)",
                (user.id, user.fullname, user.age, user.number)
            )
            await db.commit()

    async def edit_user(self, user: User):
        async with aiosqlite.connect(self.path) as db:
            prev = await self.get_user(user.id)

            if user.fullname is None:
                user.fullname = prev.fullname
            if user.age is None:
                user.age = prev.age
            if user.number is None:
                user.number = prev.number

            await db.execute(
                "UPDATE users SET fullname = ?, age = ?, number = ? WHERE id = ?",
                (user.fullname, user.age, user.number, user.id)
            )
            await db.commit()



    async def create_tasks_table(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY NOT NULL,
            user_id INTEGER,
            task TEXT
        );''')
            await db.commit()


    async def add_task(self, task: AddTask):
        async with aiosqlite.connect(self.path) as db:
            sql = """
            INSERT INTO tasks (user_id, task)
            VALUES (:user_id, :task);
        """
        params = {
            "user_id": task.user_id,
            "task": task.task
        }
        await db.execute(sql, params)
        await db.commit()

    async def get_tasks(self, user_id: int) -> list[AddTask]:
        async with aiosqlite.connect(self.path) as db:
            sql = "SELECT * FROM tasks WHERE user_id = ?;"
            params = (user_id,)
            cursor = await db.execute(sql, params)
            rows = await cursor.fetchall()
        
            tasks = []
            for row in rows:
                tasks.append(AddTask(id=row[0], user_id=row[1], task=row[2]))
        
        return tasks

    async def delete_task(self, task_id: int):
        async with aiosqlite.connect(self.path) as db:
            sql = "DELETE FROM tasks WHERE id = ?;"
        params = (task_id,)
        await db.execute(sql, params)
        await db.commit()

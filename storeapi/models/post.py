from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    id: int

    class config:
        orm_mode = True


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    id: int

    class config:
        orm_mode = True


class UserPostwithComments(BaseModel):
    post: UserPost
    comments: list[Comment]

from fastapi import HTTPException, Path, status, Depends
import routers.users as deps
import routers.posts as posts
async def post_dependency_check(post_id: int = Path(default=None), owner: deps.User = Depends(deps.get_current_active_user)):
    if post_id not in posts.fake_blog_db:
        raise HTTPException(detail="the data with these id does not exist", status_code=status.HTTP_404_NOT_FOUND)
    post_data = posts.fake_blog_db[post_id]
    if post_data["owner"] != owner.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not the owner of these post")
    return post_id

from src.database import db
from src.models import User, Session, Post, Board, FileTracker, FileRefference
from src.engine.utils import hash_password


def register_user(login, password):
    if User.query.filter_by(login=login).first():
        raise ValueError("This login is busy")

    pass_hash = hash_password(login, password)
    new_user = User(
        login=login,
        pass_hash=pass_hash
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user
    

def login_user(login, password, ip, user_agent):
    pass_hash = hash_password(login, password)
    current_user = User.query.filter_by(
        login=login,
        pass_hash=pass_hash
    ).first()

    if not current_user:
        raise ValueError("No such user")

    current_session = Session.query.filter_by(
        user=current_user,
        user_agent=user_agent,
        ip=ip
    ).first()

    if current_session:
        return current_session.id, current_session.token

    new_session = Session(
        user=current_user,
        user_agent=user_agent,
        ip=ip
    )
    db.session.add(new_session)
    db.session.commit()
    return new_session.id, new_session.token


def associate_with_post(files, post):
    filetrackers = list(map(
        lambda id:
            FileTracker.query.filter_by(id=id).first(),
        files
    ))

    file_refferences = list(map(
        lambda filetracker:
            FileRefference(
                post=post,
                filetracker=filetracker
            ),
        filetrackers
    ))

    db.session.add_all(file_refferences)
    db.session.commit()


def get_thread_of_post(post):
    current_post = post
    # 1 -- GENESIS POST ID
    while(current_post.parent and current_post.parent.id != 1):
        current_post = Post.query.filter_by(id=current_post.parent.id).first()
        if not current_post:
            return None
    return current_post


def get_threads_preview_dumped(board):
    return list(map(
        lambda post:
            post.dump_to_dict(with_children=True, child_number=3),
        Post.query.filter_by(
            # GENESIS POST ID
            parent_id=1,
            board=board
        ).all()
    ))


def get_boards_dumped():
    return list(map(
        lambda board:
            board.dump_to_dict(),
        Board.query.all()
    ))


def get_board_by_short(short):
    return Board.query.filter_by(short=short).first()


def get_post_by_id(id):
    return Post.query.filter_by(id=id).first()


def get_posts_in_thread_dumped(thread_post):
    posts_in_thread = list(filter(
        lambda post:
            get_thread_of_post(post) == thread_post and post != thread_post,
        Post.query.all()    
    ))

    return list(map(
        lambda post:
            post.dump_to_dict(),
        posts_in_thread
    ))
    

def get_last_upload_id():
    last_element = FileTracker.query.order_by(FileTracker.id.desc()).first()
    if not last_element:
        return 0
    else:
        return last_element.id



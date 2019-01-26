import os
from config import Config
from src.database import db
from src.database import User, Session, Post, Board, FileTracker, FileRefference
from src.engine.utils import hash_password
from src.utils import Utils

class Engine:
    @staticmethod
    def get_board_by_short(short):
        return Board.query.filter_by(short=short).first()


    @staticmethod
    def get_post_by_id(id):
        return Post.query.filter_by(id=id).first()


    @staticmethod
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
        

    @staticmethod
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


    @staticmethod
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


    @staticmethod
    def get_thread_of_post(post):
        current_post = post
        # 1 -- GENESIS POST ID
        while(current_post.parent and current_post.parent.id != 1):
            current_post = Post.query.filter_by(id=current_post.parent.id).first()
            if not current_post:
                return None
        return current_post


    @staticmethod
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


    @staticmethod
    def get_boards_dumped():
        return list(map(
            lambda board:
                board.dump_to_dict(),
            Board.query.all()
        ))


    @staticmethod
    def get_posts_in_thread_dumped(thread_post):
        posts_in_thread = list(filter(
            lambda post:
                Engine.get_thread_of_post(post) == thread_post and post != thread_post,
            Post.query.all()    
        ))

        return list(map(
            lambda post:
                post.dump_to_dict(),
            posts_in_thread
        ))
        

    @staticmethod
    def get_last_upload_id():
        last_element = FileTracker.query.order_by(FileTracker.id.desc()).first()
        if not last_element:
            return 0
        else:
            return last_element.id


    @staticmethod
    def save_image(file, id, ext):
        save_path = os.path.join(Config.FLASK_CONFIG["UPLOAD_FOLDER"], "%s.%s" % (id, ext))  
        file.save(save_path)
        info = "Image - %sb, %spx" % (
            Utils.get_file_size(save_path),
            Utils.get_file_resolution(save_path)
        )
        return save_path, save_path, info


    @staticmethod
    def save_video(file, id, ext):
        save_path = os.path.join(Config.FLASK_CONFIG["UPLOAD_FOLDER"], "%s.%s" % (id, ext))  
        preview_path = os.path.join(Config.FLASK_CONFIG["UPLOAD_FOLDER"], "%s_preview.png" % (id)) 
        file.save(save_path)
        Utils.cut_first_frame(save_path, preview_path)
        info = "Video - %sb, %spx, %ss" % (
            Utils.get_file_size(save_path),
            Urils.get_file_resolution(save_path),
            Utils.get_media_length(save_path)
        )
        return save_path, preview_path, info


    @staticmethod
    def save_music(file, id, ext):
        save_path = os.path.join(Config.FLASK_CONFIG["UPLOAD_FOLDER"], "%s.%s" % (id, ext)) 
        preview_path = Config.MUSIC_RREVIEW_PATH
        file.save(save_path)
        info = "Audio - %sb, %spx, %ss" % (
            Utils.get_file_size(save_path),
            Urils.get_file_resolution(save_path),
            Utils.get_media_length(save_path)
        )
        return save_path, preview_path, info
        

    @staticmethod
    def upload_file(files, board_short):
        file = files.get('file')

        if (not file) or (not file.filename):
            raise ValueError()

        board = Board.query.filter_by(short=board_short).first()
        if not board:
            raise ValueError()

        filename = file.filename
        file_id = Engine.get_last_upload_id() + 1
        file_ext = Utils.get_ext(filename)

        file_path = None
        preview_path = None 
        info = None
        if file_ext in Utils.VIDEOS_EXTS:
            file_path, preview_path, info = Engine.save_video(file, file_id, file_ext)
        elif file_ext in Utils.IMAGES_EXTS:
            file_path, preview_path, info = Engine.save_image(file, file_id, file_ext)
        elif file_ext in Utils.MUSICS_EXTS:
            file_path, preview_path, info = Engine.save_music(file, file_id, file_ext)

        filetracker = FileTracker(
            file_path=file_path,
            preview_path=preview_path,
            info=info,
            board=board
        )
        db.session.add(filetracker)
        db.session.commit()

        return {
            'filename': filetracker.file_path,
            'id': filetracker.id
        }

        



        

        




from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, make_response, Blueprint
from config import Config
from src.engine import get_board_by_short, get_boards_dumped, get_threads_preview_dumped
from src.server.utils import session_checker

app = Blueprint('frontend', __name__, template_folder=Config.TEMPLATES_DIR)

@app.route('/<board_short>')
@session_checker()
def board_handle(board_short):
    current_board = get_board_by_short(board_short)

    return render_template(
        'board.html', 
        current_board=current_board,
        boards=get_boards_dumped(),
        posts=get_threads_preview_dumped(current_board)
    )
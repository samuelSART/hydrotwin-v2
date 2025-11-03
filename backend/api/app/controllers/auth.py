import logging

from flask import Blueprint, request, session, redirect, url_for, current_app, jsonify
from cas import CASClient

auth_bp = Blueprint('auth', __name__)

cas_client = CASClient(
    version=3,
    server_url = current_app.config['CAS_AUTH_SERVER'],
    service_url = current_app.config['CAS_SERVICE_URL']
)


@auth_bp.route('/profile')
def profile(method=['GET']):
    if 'username' in session:
        return f"Logged in as {session['username']}. <a href=\"{url_for('auth.logout')}\">Logout</a>"
    return f"Login required. <a href=\"{url_for('auth.login')}\">Login</a>", 403

@auth_bp.route('/verify', methods=['GET'])
def verify():
    try:
        if 'username' in session:
            return jsonify({'status': 200, 'data': {'username': session['username']}, 'ok': True})
        else:
            cas_login_url = cas_client.get_login_url()
            logging.debug('[verify] CAS login URL: %s', cas_login_url)
            return jsonify({'status': 401, 'cas_url': cas_login_url, 'title': 'Unauthorized', 'detail': 'Login required', 'ok': False}), 401
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@auth_bp.route('/login')
def login():
    next = request.args.get('next')
    ticket = request.args.get('ticket')
    if not ticket:
        # No ticket, the request come from end user, send to CAS login
        cas_login_url = cas_client.get_login_url()
        logging.debug('CAS login URL: %s', cas_login_url)
        return redirect(cas_login_url)

    # There is a ticket, the request come from CAS as callback.
    # need call `verify_ticket()` to validate ticket and get user profile.
    logging.debug('ticket: %s', ticket)
    logging.debug('next: %s', next)

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    logging.debug(
        'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)
    
    if user:
        session['username'] = user

    return redirect("/")

@auth_bp.route('/logout')
def logout():
    try:
        if 'username' in session:
            redirect_url = url_for('auth.logout_callback', _external=True)
            cas_logout_url = cas_client.get_logout_url(redirect_url)
            
            logging.debug('CAS redirect_url URL: %s', redirect_url)
            logging.debug('CAS logout URL: %s', cas_logout_url)

            session.pop('username', None)
            
            return jsonify({'status': 200, 'data': {'cas_logout_url': cas_logout_url}, 'ok': True})
        else:
            return jsonify({'status': 200, 'data': {'cas_logout_url': None}, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@auth_bp.route('/logout_callback')
def logout_callback():
    logging.debug('CAS logout_callback')
    # redirect from CAS logout request after CAS logout successfully
    if 'username' in session:
        session.pop('username', None)
        
    return redirect("/")


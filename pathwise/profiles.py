"""Optional persistent profiles through Supabase Auth + row-level secured table."""
import streamlit as st

FIELDS = ('name','career_goal','interests','completed_prerequisites','skills','readiness')

def configured():
    try:
        return bool(st.secrets.get('SUPABASE_URL') and st.secrets.get('SUPABASE_ANON_KEY'))
    except (FileNotFoundError, KeyError):
        return False

def client():
    from supabase import create_client
    return create_client(st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_ANON_KEY'])

def authenticate(email, password, register=False):
    try:
        db = client()
        if register:
            result = db.auth.sign_up({'email': email, 'password': password})
        else:
            result = db.auth.sign_in_with_password({'email': email, 'password': password})
    except Exception as exc:
        # Display only a safe error category and standard Supabase Auth metadata.
        # Never print request headers, credentials, tokens, or raw exception details.
        error_type = type(exc).__name__
        error_code = getattr(exc, 'code', None)
        status = getattr(exc, 'status', None)
        details = [f'Error type: {error_type}']
        if isinstance(status, int):
            details.append(f'HTTP status: {status}')
        if isinstance(error_code, str) and error_code.replace('_', '').isalnum() and len(error_code) < 80:
            details.append(f'Error code: {error_code}')
        st.error('Supabase authentication diagnostic — ' + ' | '.join(details))
        raise

    if result.session:
        st.session_state['pw_auth'] = {'access_token':result.session.access_token,
            'refresh_token':result.session.refresh_token,'user_id':result.user.id,'email':email}
    return result

def authorized_client():
    db=client()
    session=st.session_state['pw_auth']
    response=db.auth.set_session(session['access_token'],session['refresh_token'])
    if response.session:
        session['access_token']=response.session.access_token
        session['refresh_token']=response.session.refresh_token
    return db

def load_profile():
    db=authorized_client()
    uid=st.session_state['pw_auth']['user_id']
    rows=db.table('student_profiles').select('profile').eq('user_id',uid).execute().data
    return rows[0]['profile'] if rows else None

def save_profile(profile):
    db=authorized_client()
    uid=st.session_state['pw_auth']['user_id']
    clean={k:profile[k] for k in FIELDS}
    db.table('student_profiles').upsert({'user_id':uid,'profile':clean},on_conflict='user_id').execute()

def logout():
    st.session_state.pop('pw_auth',None)
    st.session_state.pop('pw_saved_profile',None)
    st.session_state.pop('pw_profile_mode',None)

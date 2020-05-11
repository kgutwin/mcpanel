import os
import os.path


def render(template, **kwargs):
    with open(os.path.join(os.path.dirname(__file__), template)) as fp:
        __body = fp.read()
    locals().update(kwargs)
    return eval(f'f"""{__body}"""')


def admin(body):
    return render(
        'base.html',
        emoji='1f3de',
        title='Minecraft Server Admin',
        body=body
    )


def admin_login(error_message=''):
    body = render('admin-login.html', error_message=error_message)
    return admin(body)


def admin_mcstatus(mcstatus=None):
    if mcstatus is None:
        return ""

    return render('admin-page-mcstatus.html', status=mcstatus)

def admin_page(leaderkey, instance_state={'Name': 'unknown'}, mcstatus=None,
               response=''):
    rendered_mcstatus = admin_mcstatus(mcstatus)
    
    body = render(
        'admin-page.html',
        leaderkey=leaderkey,
        instance_id=os.environ['INSTANCE_ID'],
        instance_state=instance_state,
        mcstatus=rendered_mcstatus,
        response=response,
    )
    return admin(body)


def error(message):
    return render(
        'base.html',
        emoji='26A0',
        title='Error',
        body=message
    )

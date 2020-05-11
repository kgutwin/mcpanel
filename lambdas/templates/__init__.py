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
        title='Admin',
        body=body
    )


def admin_login(error_message=''):
    body = render('admin-login.html', error_message=error_message)
    return admin(body)


def admin_page(leaderkey, instance_state={'Name': 'unknown'}, response=''):
    body = render(
        'admin-page.html',
        leaderkey=leaderkey,
        instance_id=os.environ['INSTANCE_ID'],
        instance_state=instance_state,
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

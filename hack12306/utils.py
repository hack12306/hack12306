# encoding: utf8

def cookie_str_to_dict(cookie_str):
    cookies = []
    for cookie in [cookie.strip() for cookie in cookie_str.split(';')]:
        cookies.append(cookie.split('='))
    return dict(cookies)

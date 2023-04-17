from random import choice
from typing import Union
from playwright.sync_api import Page
from faker import Faker
from allure import step

from form_fields import (get_name,
                         get_company,
                         get_boundary_name,
                         get_boundary_company,
                         bad_field_generator)

fake = Faker('ru_RU')


SELECTORS = {
    'NAME': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[1]/input',
    'EMAIL': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[2]/input',
    'COMPANY': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[3]/input',
    'DEPARTMENT': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[4]/select',
    'PHONE': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[5]/input',
    'MESSENGER': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[6]/label',
    'TELEGRAM': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[7]/label[1]',
    'WHATSAPP': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[7]/label[2]',
    'AGREEMENT': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[8]/label',
    'MAIL_LIST': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[9]/label',
    'SEND': '//*[@id="LP-79060w4"]/div[2]/div/div[1]/div/form/div/div[10]/button',
}


DEPARTMENTS = ('PR и маркетинг', 'Риски и безопасность', 'Другое')


@step("Перейти на страницу scan-interfax.ru и открыть форму.")
def open_form(page: Page):
    page.goto("https://scan-interfax.ru/")
    page.wait_for_load_state(state='networkidle')
    page.click('//*[@id="primary"]/div/section[1]/div/div[1]/div/button')
    if not page.get_by_text('Заявка на тестовый доступ к SCAN').is_visible():
        page.reload(timeout=5000)
        page.wait_for_timeout(5000)
        page.click('//*[@id="primary"]/div/section[1]/div/div[1]/div/button')


@step("Заполнить текстовые поля формы запроса тестового доступа.")
def fill_form(page: Page, name: Union[str, int], company: Union[str, int]):
    if name == 'basic':
        page.fill(selector=SELECTORS.get('NAME'), value=get_name())
    else:
        page.fill(selector=SELECTORS.get('NAME'),
                  value=get_boundary_name(name))
    page.fill(selector=SELECTORS.get('EMAIL'), value=fake.email())
    if company == 'basic':
        page.fill(selector=SELECTORS.get('COMPANY'), value=get_company())
    else:
        page.fill(selector=SELECTORS.get('COMPANY'),
                  value=get_boundary_company(company))

    page.select_option(selector=SELECTORS.get('DEPARTMENT'),
                       value=choice(DEPARTMENTS))
    page.fill(selector=SELECTORS.get('PHONE'), value=fake.phone_number())


@step("Согласиться на обработку персональных данных.")
def set_checked_agreement(page):
    page.set_checked(selector=SELECTORS.get('AGREEMENT'), checked=True)


@step("Согласиться подписаться на рассылку.")
def set_checked_mailing(page):
    page.set_checked(selector=SELECTORS.get('MAIL_LIST'), checked=True)


@step("Заполнить форму, оставив пустым выбранное поле.")
def missing_field_form(page: Page, exclude: str):
    if not exclude == 'name':
        page.fill(selector=SELECTORS.get('NAME'), value=get_name())
    elif not exclude == 'company':
        page.fill(selector=SELECTORS.get('COMPANY'), value=get_company())
    elif not exclude == 'department':
        page.select_option(selector=SELECTORS.get('DEPARTMENT'),
                           value=choice(DEPARTMENTS))
    elif not exclude == 'phone':
        page.fill(selector=SELECTORS.get('PHONE'), value=fake.phone_number())
    elif not exclude == 'email':
        page.fill(selector=SELECTORS.get('EMAIL'), value=fake.email())


@step("""Заполнить форму, одно поле заполнено некорректно
    (с латинскими буквами, цифрами и специальными символами).""")
def bad_field_form(page: Page, field: str):
    if field == 'name':
        page.fill(selector=SELECTORS.get('NAME'), value=bad_field_generator())
    else:
        page.fill(selector=SELECTORS.get('NAME'), value=get_name())
    if field == 'company':
        page.fill(selector=SELECTORS.get('COMPANY'), value=bad_field_generator())
    else:
        page.fill(selector=SELECTORS.get('COMPANY'), value=get_company())
    page.select_option(selector=SELECTORS.get('DEPARTMENT'),
                       value=choice(DEPARTMENTS))
    if field == 'phone':
        page.fill(selector=SELECTORS.get('PHONE'), value=bad_field_generator())
    else:
        page.fill(selector=SELECTORS.get('PHONE'), value=fake.phone_number())


@step("Согласиться на связь в выбранном мессенджере.")
def choose_messenger(page: Page, messenger: str):
    page.set_checked(selector=SELECTORS.get('MESSENGER'), checked=True)
    page.set_checked(selector=SELECTORS.get(messenger), checked=True)


@step("Отправить форму нажатием на кнопку 'Заказать тестовый доступ'.")
def send_form(page: Page):
    page.click(selector=SELECTORS.get('SEND'))


@step("Ожидаемый результат: форма отправлена, пользователь видит модальное "
      "окно с текстом 'Спасибо за вашу заявку!'.")
def form_sent_assertion(page: Page):
    assert page.get_by_text('Спасибо за вашу заявку!').is_visible(timeout=500)


@step("Ожидаемый результат: форма не отправлена, пользователь по-прежнему "
      "видит модальное окно с заголовком 'Заявка на тестовый доступ к SCAN'.")
def form_not_sent_assertion(page: Page):
    assert page.get_by_text(
        'Заявка на тестовый доступ к SCAN').is_visible(timeout=500)


# CORRECTLY FILLED FORM TESTS


def test_correct_form_with_agreement(page: Page) -> None:
    """Проверка верно заполненной формы с согласием на обработку ПД."""
    open_form(page)
    fill_form(page=page, name='basic', company='basic')
    set_checked_agreement(page)
    send_form(page)
    form_sent_assertion(page)


def test_correct_form_with_agreement_and_mail_list(page: Page) -> None:
    """Проверка верно заполненной формы с согласиями на обработку ПД
     и подписку на рассылку."""
    open_form(page)
    fill_form(page=page, name='basic', company='basic')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_sent_assertion(page)


def test_correct_form_with_agreement_and_mail_list_and_telegram(page: Page):
    """Проверка верно заполненной формы с согласиями на обработку ПД,
    подписку на рассылку и на связь в Telegram."""
    open_form(page)
    fill_form(page=page, name='basic', company='basic')
    set_checked_agreement(page)
    set_checked_mailing(page)
    choose_messenger(page=page, messenger='TELEGRAM')
    send_form(page)
    form_sent_assertion(page)


def test_correct_form_with_agreement_and_mail_list_and_whatsapp(page: Page):
    """Проверка верно заполненной формы с согласиями на обработку ПД,
    подписку на рассылку и на связь в WhatsApp."""
    open_form(page)
    fill_form(page=page, name='basic', company='basic')
    set_checked_agreement(page)
    set_checked_mailing(page)
    choose_messenger(page=page, messenger='WHATSAPP')
    send_form(page)
    form_sent_assertion(page)


# LONG FIELD NAMES TESTS


def test_long_name_255(page: Page):
    """Проверка формы с полем "Ваши ФИО" длиной 255 символов."""
    open_form(page)
    fill_form(page=page, name=255, company='basic')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_sent_assertion(page)


def test_long_name_256(page: Page):
    """Проверка с полем "Ваши ФИО" максимальной длины."""
    open_form(page)
    fill_form(page=page, name=256, company='basic')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_sent_assertion(page)


def test_long_name_257(page: Page):
    """Проверка формы с полем "Ваши ФИО", превышающим допустимую длину."""
    open_form(page)
    fill_form(page=page, name=257, company='basic')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_long_company_255(page: Page):
    """Проверка формы с полем "Компания" длиной 255 символов."""
    open_form(page)
    fill_form(page=page, name='basic', company=255)
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_sent_assertion(page)


def test_long_company_256(page: Page):
    """Проверка формы с полем "Компания" максимальной длины."""
    open_form(page)
    fill_form(page=page, name='basic', company=256)
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_sent_assertion(page)


def test_long_company_257(page: Page):
    """Проверка формы с полем "Компания", превышающим допустимую длину."""
    open_form(page)
    fill_form(page=page, name='basic', company=257)
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


# MISSING FIELDS TESTS


def test_form_without_name(page: Page):
    """Проверка формы с пустым полем "Ваши ФИО"."""
    open_form(page)
    missing_field_form(page=page, exclude='name')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_form_without_company(page: Page):
    """Проверка формы с пустым полем "Компания"."""
    open_form(page)
    missing_field_form(page=page, exclude='company')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_form_without_department(page: Page):
    """Проверка формы без выбранного подразделения."""
    open_form(page)
    missing_field_form(page=page, exclude='department')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_form_without_phone(page: Page):
    """Проверка формы с пустым полем "Телефон"."""
    open_form(page)
    missing_field_form(page=page, exclude='phone')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_form_without_email(page: Page):
    """Проверка формы с пустым полем "Ваш корпоративный email"."""
    open_form(page)
    missing_field_form(page=page, exclude='email')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_form_without_agreement(page: Page) -> None:
    """Проверка формы без согласия на обработку ПД."""
    open_form(page)
    fill_form(page=page, name='basic', company='basic')
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_empty_form(page: Page):
    """Проверка пустой формы."""
    open_form(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_empty_form_with_agreement(page: Page):
    """Проверка пустой формы с согласием на обработку ПД."""
    open_form(page)
    set_checked_agreement(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_empty_form_with_agreement_and_mail_list(page: Page):
    """Проверка пустой формы с согласиями на обработку ПД и рассылку."""
    open_form(page)
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


# BAD NAMES TESTS


def test_bad_name(page: Page):
    """Проверка формы с некорректным полем "Ваши ФИО"."""
    open_form(page)
    bad_field_form(page, field='name')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_bad_company(page: Page):
    """Проверка формы с некорректным полем "Компания"."""
    open_form(page)
    bad_field_form(page, field='company')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_bad_email(page: Page):
    """Проверка формы с некорректным полем "Ваш корпоративный email"."""
    open_form(page)
    bad_field_form(page, field='email')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)


def test_bad_phone(page: Page):
    """Проверка формы с некорректным полем "Телефон"."""
    open_form(page)
    bad_field_form(page, field='phone')
    set_checked_agreement(page)
    set_checked_mailing(page)
    send_form(page)
    form_not_sent_assertion(page)

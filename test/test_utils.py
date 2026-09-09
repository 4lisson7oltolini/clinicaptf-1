from utils import (
    limpar_numeros,
    validar_cpf,
    formatar_cpf,
    formatar_cep,
    validar_email,
)


def test_limpar_numeros():
    assert limpar_numeros("123.456.789-00") == "12345678900"


def test_cpf_valido():
    assert validar_cpf("529.982.247-25") is True


def test_cpf_invalido():
    assert validar_cpf("111.111.111-11") is False


def test_formatar_cpf():
    assert formatar_cpf("52998224725") == "529.982.247-25"


def test_formatar_cep():
    assert formatar_cep("88330000") == "88330-000"


def test_email_valido():
    assert validar_email("teste@email.com") is True
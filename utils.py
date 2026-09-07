import re
import hashlib
import secrets
import requests


def limpar_numeros(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def validar_cpf(cpf: str) -> bool:
    """Valida CPF usando o algoritmo oficial de dígitos verificadores."""
    cpf = limpar_numeros(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito1 = 0 if resto == 10 else resto
    if digito1 != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito2 = 0 if resto == 10 else resto
    return digito2 == int(cpf[10])


def formatar_cpf(cpf: str) -> str:
    cpf = limpar_numeros(cpf)
    if len(cpf) != 11:
        return cpf
    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"


def formatar_cep(cep: str) -> str:
    cep = limpar_numeros(cep)
    if len(cep) != 8:
        return cep
    return f"{cep[0:5]}-{cep[5:8]}"


def validar_email(email: str) -> bool:
    """Validação simples de formato de e-mail."""
    if not email:
        return False
    padrao = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return re.match(padrao, email.strip()) is not None


def buscar_endereco_por_cep(cep: str):
    """
    Consulta o endereço de um CEP usando a API pública ViaCEP.

    Retorna (True, dados) em caso de sucesso, onde dados é um dict com
    'logradouro', 'bairro', 'localidade' (cidade) e 'uf' (estado).
    Retorna (False, mensagem_de_erro) caso o CEP seja inválido, não seja
    encontrado, ou haja falha de conexão.
    """
    cep_limpo = limpar_numeros(cep)
    if len(cep_limpo) != 8:
        return False, "Digite um CEP válido com 8 dígitos antes de buscar."

    try:
        resposta = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.exceptions.Timeout:
        return False, "A busca do CEP demorou demais. Tente novamente."
    except requests.exceptions.RequestException:
        return False, "Não foi possível consultar o CEP agora. Verifique sua conexão e tente novamente."
    except ValueError:
        return False, "A resposta do serviço de CEP veio em um formato inesperado."

    if not isinstance(dados, dict) or dados.get("erro"):
        return False, "CEP não encontrado. Verifique o número digitado."

    return True, {
        "logradouro": dados.get("logradouro", "") or "",
        "bairro": dados.get("bairro", "") or "",
        "localidade": dados.get("localidade", "") or "",
        "uf": dados.get("uf", "") or "",
    }


def hash_senha(senha: str, salt_hex: str = None):
    """
    Gera um hash seguro de senha usando PBKDF2-HMAC-SHA256 com salt aleatório.
    Retorna (hash_hex, salt_hex). Se salt_hex for informado, reusa o mesmo salt
    (usado para conferir uma senha já cadastrada).
    """
    if salt_hex is None:
        salt_hex = secrets.token_hex(16)
    salt_bytes = bytes.fromhex(salt_hex)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt_bytes, 100_000)
    return hash_bytes.hex(), salt_hex


def verificar_senha(senha: str, hash_salvo: str, salt_salvo: str) -> bool:
    """Confere se a senha informada corresponde ao hash salvo, sem timing attack."""
    hash_calculado, _ = hash_senha(senha, salt_salvo)
    return secrets.compare_digest(hash_calculado, hash_salvo)


ESTADOS_BR = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]
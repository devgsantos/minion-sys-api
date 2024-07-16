from typing import Optional

from pydantic import BaseModel


class ClienteBase(BaseModel):
    ClienteId: int
    Email: str
    Nome: str
    Logradouro: str
    NumeroEndereco: str
    Bairro: str
    Cidade: str
    UF: str
    Telefone: str
    Cpf: Optional[str] = None
    Cnpj: Optional[str] = None
    Nacionalidade: str
    Naturalidade: str
    ResponsavelCadastro: Optional[str] = None
    Status: bool

from enum import Enum


class SalesStatusEnum(Enum):
    """
    Enumeração para os status de vendas no sistema.

    Os status representam os diferentes estágios de uma venda:
    - PENDENTE: Venda esperando aprovação
    - APROVADA: Venda aprovada para processamento
    - SEPARACAO_DE_ESTOQUE: Produtos estão sendo separados do estoque
    - EM_TRANSPORTE: Venda em transporte para o cliente
    - FINALIZADA: Venda concluída com sucesso
    - ESTORNADA: Venda estornada pelo cliente
    - CANCELADA: Venda cancelada pela empresa
    """
    PENDENTE = 2
    EM_PROCESSAMENTO = 11
    APROVADA = 3
    SEPARACAO_DE_ESTOQUE = 4
    EM_TRANSPORTE = 5
    FINALIZADA = 6
    ESTORNADA = 7
    CANCELADA = 8

    @classmethod
    def get_id_by_name(cls, name):
        """Returns the status ID by name"""
        return cls[name].value
    
    @classmethod
    def get_name_by_id(cls, status_id):
        """Returns the status name by ID"""
        for status in cls:
            if status.value == status_id:
                return status.name
        return None
    
    @classmethod
    def get_all_status(cls):
        """Returns all statuses as dictionaries"""
        return [{"id": status.value, "name": status.name} for status in cls]
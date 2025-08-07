from enum import Enum


class BudgetStatusEnum(Enum):
    """
    Enumeração para os status de orçamentos no sistema.
    
    Os status representam os diferentes estágios de um orçamento:
    - COTACAO: Orçamento em fase de cotação inicial
    - APROVADO: Orçamento aprovado pelo cliente
    - AGUARDANDO_APROVACAO: Orçamento enviado e aguardando resposta do cliente
    - REPROVADO: Orçamento rejeitado pelo cliente
    """
    COTACAO = 1
    AGUARDANDO_APROVACAO = 2
    APROVADO = 3
    REPROVADO = 4
    
    @classmethod
    def get_id_by_name(cls, name):
        """Retorna o ID do status pelo nome"""
        return cls[name].value
    
    @classmethod
    def get_name_by_id(cls, status_id):
        """Retorna o nome do status pelo ID"""
        for status in cls:
            if status.value == status_id:
                return status.name
        return None
    
    @classmethod
    def get_all_status(cls):
        """Retorna todos os status como dicionários"""
        return [{"id": status.value, "name": status.name} for status in cls]
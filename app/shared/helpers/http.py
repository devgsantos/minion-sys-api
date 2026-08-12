class InvalidPaginationError(ValueError):
    pass


INTERNAL_ERROR_MESSAGE = 'Erro interno do servidor.'


def error_payload(message, data=None):
    return {
        'status': False,
        'message': message,
        'data': data,
    }


def internal_error(logger, exc):
    logger.log(message=str(exc), level='error')
    return error_payload(INTERNAL_ERROR_MESSAGE), 500


def parse_pagination(args, default_limit=10, max_limit=100):
    try:
        page = int(args.get('pagina', 1))
        limit = int(args.get('limite', default_limit))
    except (TypeError, ValueError) as exc:
        raise InvalidPaginationError(
            "'pagina' e 'limite' devem ser números inteiros."
        ) from exc

    if page < 1:
        raise InvalidPaginationError("'pagina' deve ser maior ou igual a 1.")
    if limit < 1 or limit > max_limit:
        raise InvalidPaginationError(
            f"'limite' deve estar entre 1 e {max_limit}."
        )
    return page, limit

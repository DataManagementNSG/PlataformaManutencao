def user_sector(request):
    if request.user.is_authenticated:
        try:
            return {
                'user_sector': request.user.usuario.setor.nome
            }
        except AttributeError:
            return {'user_sector': 'Desconhecido'}
    return {}

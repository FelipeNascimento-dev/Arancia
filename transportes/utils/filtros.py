from transportes.models import FiltroFavoritoUsuario, FiltroPadraoTela


def obter_filtros_tela(usuario, chave_tela: str) -> dict:
    filtro_usuario = (
        FiltroFavoritoUsuario.objects
        .filter(
            usuario=usuario,
            chave_tela=chave_tela,
            favorito=True,
            ativo=True,
        )
        .order_by("-atualizado_em")
        .first()
    )

    if filtro_usuario and isinstance(filtro_usuario.filtros, dict):
        return filtro_usuario.filtros

    filtro_padrao = (
        FiltroPadraoTela.objects
        .filter(
            chave_tela=chave_tela,
            ativo=True,
        )
        .first()
    )

    if filtro_padrao and isinstance(filtro_padrao.filtros, dict):
        return filtro_padrao.filtros

    return {}


def salvar_filtro_favorito(usuario, chave_tela: str, filtros: dict, nome="Meu filtro favorito"):
    FiltroFavoritoUsuario.objects.filter(
        usuario=usuario,
        chave_tela=chave_tela,
        favorito=True,
    ).update(favorito=False)

    obj, _ = FiltroFavoritoUsuario.objects.update_or_create(
        usuario=usuario,
        chave_tela=chave_tela,
        nome=nome,
        defaults={
            "filtros": filtros,
            "favorito": True,
            "ativo": True,
        }
    )
    return obj


def limpar_filtro_favorito(usuario, chave_tela: str):
    FiltroFavoritoUsuario.objects.filter(
        usuario=usuario,
        chave_tela=chave_tela,
        favorito=True,
    ).update(ativo=False, favorito=False)

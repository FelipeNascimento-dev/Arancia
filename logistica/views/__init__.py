from .view_base import index
<<<<<<< HEAD
from .logout_view import logout_view
from .logout_confirm_view import logout_confirm_view
from .view_consulta_id import consulta_id_form, consulta_id_table
from .view_recebimentos import pre_recebimento, recebimento
from .view_romaneio import registrar_romaneio
from .view_consulta_result import consulta_result, btn_voltar
from .view_reserva_equip import reserva_equip
from .view_saida_campo import saida_campo
from .view_consulta_ma84 import consulta_ma84, btn_ma_voltar
from .view_consulta_ec01 import consulta_ec01, btn_ec_voltar
from .view_extracao_pedidos import extracao_pedidos
from .view_ip_tracking import trackingIP
from .register_view import registrar_usuario
from .view_consulta_etiquetas import consulta_etiquetas
from .view_consulta_pedidos import consulta_pedidos
from .login_view import UserLoginView
from .configuracao_user_view import UserPasswordChangeView, settings_view
from .view_recebimento_remessa import recebimento_remessa
from .view_consulta_entrada_pedido import order_consult
from .view_detalhe_pedido import order_detail
from .view_button_desn import button_desn
from .view_order_return_check import order_return_check
from .view_user_ger import user_ger
from .view_skill_ger import skill_ger
from .view_reverse_create import reverse_create, delete_btn, cancel_btn
from .view_consult_rom import consult_rom
from .view_send_quotes import send_quotes
from .toggle_db_view import toggle_db
from .view_unsuccessful_insert import unsuccessful_insert
from .view_client_select import client_select
from .view_client_checkin import client_checkin
from .view_order_select import order_select
=======
from .views_user.logout_view import logout_view
from .views_user.logout_confirm_view import logout_confirm_view
from .view_fullfilment.view_consulta_id import consulta_id_form, consulta_id_table
from .view_fullfilment.view_recebimentos import pre_recebimento, recebimento
from .view_fullfilment.view_romaneio import registrar_romaneio
from .view_fullfilment.view_consulta_result import consulta_result, btn_voltar
from .views_fluxo_entrega.view_reserva_equip import reserva_equip
from .views_fluxo_entrega.view_saida_campo import saida_campo
from .views_fluxo_entrega.view_consulta_ma84 import consulta_ma84, btn_ma_voltar
from .views_fluxo_entrega.view_consulta_ec01 import consulta_ec01, btn_ec_voltar
from .views_fluxo_entrega.view_extracao_pedidos import extracao_pedidos
from .views_fluxo_entrega.view_ip_tracking import trackingIP
from .views_user.register_view import registrar_usuario
from .views_lastmile_consultas.view_consulta_etiquetas import consulta_etiquetas
from .views_lastmile_consultas.view_consulta_pedidos import consulta_pedidos
from .views_user.login_view import UserLoginView
from .views_user.configuracao_user_view import UserPasswordChangeView, settings_view
from .views_recebimento_estoque.view_recebimento_remessa import recebimento_remessa
from .views_lastmile_consultas.view_consulta_entrada_pedido import order_consult
from .views_lastmile_consultas.view_detalhe_pedido import order_detail
from .views_fluxo_entrega.view_button_desn import button_desn
from .views_fluxo_retirada.view_conferir_retirada import order_return_check
from .views_gerenciamento.view_gestao_usuarios import user_ger
from .views_gerenciamento.view_gestao_skills import skill_ger
from .views_reverse.view_criar_reversa import reverse_create, delete_btn, cancel_btn
from .views_reverse.view_consulta_romaneio import consult_rom
from .views_reverse.view_enviar_cotacao import send_quotes
from .views_user.toggle_db_view import toggle_db
from .views_fluxo_entrega.view_insucesso import unsuccessful_insert
from .views_checkin_checkout.view_checkin_iniciar import client_select
from .views_checkin_checkout.view_checkin_registrar import client_checkin
from .views_checkin_checkout.view_consulta_produtos import product_create
from .views_checkin_checkout.view_consulta_clientes import client_consult
from .views_recebimento_estoque.view_gerenciamento_estoque import gerenciamento_estoque
from .views_recebimento_estoque.view_gerenciamento_kits import gerenciamento_kits
>>>>>>> release7-MERGE

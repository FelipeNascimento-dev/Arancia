//localStorage.clear();

document.addEventListener('DOMContentLoaded', function () {
  // MENU DROPDOWN PRINCIPAL (ex: Operações)
  // Dropdown principal: Operações
  const dropBtn = document.querySelector('.dropbtn');
  const dropContent = document.querySelector('.dropdown-content');

  if (dropBtn && dropContent) {
    dropBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      // Fecha todos os outros dropdowns abertos
      document.querySelectorAll('.dropdown-content').forEach(el => {
        if (el !== dropContent) el.classList.remove('show');
      });

      // Alterna o dropdown atual
      dropContent.classList.toggle('show');
    });

    document.addEventListener('click', function (e) {
      if (!dropContent.contains(e.target) && !dropBtn.contains(e.target)) {
        dropContent.classList.remove('show');
      }
    });
  }

  // SUBMENUS (ex: Pesquisas, Relatórios)
  document.querySelectorAll('.column-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
      const targetId = toggle.getAttribute('data-target');
      const targetMenu = document.getElementById(targetId);

      document.querySelectorAll('.submenu').forEach(menu => {
        if (menu !== targetMenu) {
          menu.style.display = 'none';
        }
      });

      if (targetMenu) {
        targetMenu.style.display = targetMenu.style.display === 'flex' ? 'none' : 'flex';
      }
    });
  });

  // SUB-SUBMENUS (ex: Entrada-Fulfillment, Saída para Campo)
  document.querySelectorAll('.submenu-toggle').forEach(subToggle => {
    subToggle.addEventListener('click', () => {
      const subId = subToggle.getAttribute('data-target');
      const subMenu = document.getElementById(subId);
      if (subMenu) {
        subMenu.style.display = subMenu.style.display === 'block' ? 'none' : 'block';
      }
    });
  });

  // TOGGLE USUÁRIO
  const usuarioBtn = document.querySelector('.usuario-logado');
  const usuarioMenu = document.getElementById('usuario-menu');

  if (usuarioBtn && usuarioMenu) {
    usuarioBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      const isVisible = usuarioMenu.style.display === 'block';
      usuarioMenu.style.display = isVisible ? 'none' : 'block';
    });

    document.addEventListener('click', function (e) {
      if (!usuarioMenu.contains(e.target) && !usuarioBtn.contains(e.target)) {
        usuarioMenu.style.display = 'none';
      }
    });
  }

  // ETAPAS LOGÍSTICA
  const triggers = document.querySelectorAll(".etapa-trigger");
  const containers = document.querySelectorAll(".etapas-container");

  triggers.forEach(trigger => {
    trigger.addEventListener("click", () => {
      const targetId = trigger.dataset.target;
      containers.forEach(container => {
        if (container.id === targetId) {
          container.classList.toggle("active");
        } else {
          container.classList.remove("active");
        }
      });
    });
  });

  document.querySelectorAll(".etapa").forEach(etapa => {
    etapa.addEventListener("click", () => {
      etapa.parentElement.querySelectorAll(".etapa").forEach(e => e.classList.remove("ativa"));
      etapa.classList.add("ativa");
    });
  });

  // DATA E HORA
  const dataInput = document.getElementById('data');
  const horaInput = document.getElementById('hora');
  if (dataInput && horaInput) {
    function atualizarDataHora() {
      const agora = new Date();
      dataInput.value = agora.toLocaleDateString('pt-BR');
      horaInput.value = agora.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    }
    atualizarDataHora();
    setInterval(atualizarDataHora, 1000);
  }

  // ROMANEIOS
  const formulario = document.getElementById('form-romaneio');
  const btnRegistrar = document.getElementById('btn-registrar');
  const contadorDisplay = document.getElementById('contador');
  const tituloRomaneio = document.getElementById('titulo-romaneio');
  const modal = document.getElementById('modal-romaneio');
  const btnRevisar = document.getElementById('btn-revisar');
  const btnFecharModal = document.getElementById('btn-fechar-modal');
  const btnEncerrar = document.getElementById('btn-encerrar');
  const btnNaoEditar = document.getElementById('btn-nao-editar');

  if (formulario && contadorDisplay && tituloRomaneio) {
    let contadorRegistros = 0;
    let contadorRomaneio;
    const modoEdicao = localStorage.getItem('modoEdicao') === 'true';
    const romaneios = JSON.parse(localStorage.getItem('romaneios') || '{}');

    if (modoEdicao) {
      contadorRomaneio = Number(localStorage.getItem('romaneioEmEdicao')) || 1;
    } else {
      const numerosExistentes = Object.keys(romaneios).map(r => Number(r));
      const proximoNumero = numerosExistentes.length ? Math.max(...numerosExistentes) + 1 : 1;
      contadorRomaneio = proximoNumero;
      localStorage.setItem('romaneioEmEdicao', contadorRomaneio.toString().padStart(10, '0'));
    }

    function atualizarTituloRomaneio() {
      const numeroFormatado = contadorRomaneio.toString().padStart(10, '0');
      tituloRomaneio.textContent = `Romaneio ${numeroFormatado}`;
    }

    function atualizarContador() {
      contadorDisplay.textContent = `${contadorRegistros.toString().padStart(2, '0')}/30`;
    }

    function validarCampos() {
      const campos = formulario.querySelectorAll('input[required]');
      for (let campo of campos) {
        if (campo.offsetParent === null || campo.disabled) continue;
        if (!campo.value.trim()) {
          alert('Preencha todos os campos obrigatórios.');
          campo.focus();
          return false;
        }
      }
      return true;
    }

    function coletarDadosFormulario() {
      return {
        romaneio: contadorRomaneio.toString().padStart(10, '0'),
        serial: document.getElementById('serial')?.value || '',
        chamado: document.getElementById('chamado')?.value || '',
        data: document.getElementById('data')?.value || '',
        hora: document.getElementById('hora')?.value || '',
        usuario: document.getElementById('usuario')?.value || '',
        filial: document.getElementById('filial')?.value || '',
        destino: document.getElementById('destino')?.value || ''
      };
    }

    btnRegistrar?.addEventListener('click', function (e) {
      e.preventDefault();
      if (!validarCampos()) return;

      const dados = coletarDadosFormulario();
      const numeroRomaneioAtual = contadorRomaneio.toString().padStart(10, '0');
      const romaneiosObj = JSON.parse(localStorage.getItem('romaneios') || '{}');

      if (!romaneiosObj[numeroRomaneioAtual]) romaneiosObj[numeroRomaneioAtual] = [];
      romaneiosObj[numeroRomaneioAtual].push(dados);
      localStorage.setItem('romaneios', JSON.stringify(romaneiosObj));

      contadorRegistros++;
      atualizarContador();

      if (contadorRegistros >= 31 && modal) modal.style.display = 'flex';

      formulario.reset();
    });

    btnEncerrar?.addEventListener('click', function () {
      if (contadorRegistros === 0) {
        alert('Você ainda não registrou nenhum item neste romaneio.');
        return;
      }
      if (modal) modal.style.display = 'flex';
      if (contadorRegistros >= 31) {
        alert('Este romaneio já atingiu o limite de 30 registros.');
      }
    });

    async function obterEstadoDoUsuario() {
      try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        return data.region_code || 'XX';
      } catch (error) {
        console.error('Erro ao obter localização do usuário:', error);
        return 'XX';
      }
    }

    function gerarCodigoRastreio(siglaEstado) {
      const agora = new Date();
      const dia = String(agora.getDate()).padStart(2, '0');
      const mes = String(agora.getMonth() + 1).padStart(2, '0');
      const ano = String(agora.getFullYear()).slice(-2);
      const hora = String(agora.getHours()).padStart(2, '0');
      const minuto = String(agora.getMinutes()).padStart(2, '0');
      return `${siglaEstado.toUpperCase()}${dia}${mes}${ano}${hora}${minuto}BR`;
    }

    async function finalizarRomaneio() {
      const siglaEstado = await obterEstadoDoUsuario();
      const codigoRastreio = gerarCodigoRastreio(siglaEstado);
      const numeroRomaneioAtual = contadorRomaneio.toString().padStart(10, '0');

      const metadados = JSON.parse(localStorage.getItem('metadadosRomaneios') || '{}');
      metadados[numeroRomaneioAtual] = {
        codigoRastreio,
        dataCriacao: new Date().toISOString()
      };
      localStorage.setItem('metadadosRomaneios', JSON.stringify(metadados));

      contadorRegistros = 0;
      contadorRomaneio++;
      localStorage.setItem('romaneioEmEdicao', contadorRomaneio.toString().padStart(10, '0'));
      atualizarContador();
      atualizarTituloRomaneio();
    }

    btnFecharModal?.addEventListener('click', async () => {
      modal.style.display = 'none';
      await finalizarRomaneio();
    });

    btnNaoEditar?.addEventListener('click', finalizarRomaneio);

    btnRevisar?.addEventListener('click', function () {
      localStorage.setItem('modoEdicao', 'true');
      localStorage.setItem('romaneioEmEdicao', contadorRomaneio.toString().padStart(10, '0'));
      window.location.href = 'revisar.html';
    });

    atualizarContador();
    atualizarTituloRomaneio();
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("toggle-sidebar");
  const sidebar = document.querySelector(".sidebar");

  toggleBtn.addEventListener("click", function () {
    sidebar.classList.toggle("colapsada");

    if (sidebar.classList.contains("colapsada")) {
      toggleBtn.classList.replace("fa-angles-left", "fa-angles-right");
    } else {
      toggleBtn.classList.replace("fa-angles-right", "fa-angles-left");
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".sidebar");
  const toggleBtn = document.getElementById("toggle-sidebar");

  document.querySelectorAll(".dropbtn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const dropdown = btn.nextElementSibling;

      if (sidebar.classList.contains("colapsada")) {
        sidebar.classList.remove("colapsada");
        toggleBtn.classList.replace("fa-angles-right", "fa-angles-left");
      }

      dropdown.classList.toggle("show");
    });
  });

  document.querySelectorAll(".submenu-toggle").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const targetId = toggle.dataset.target;
      const submenu = document.getElementById(targetId);
      if (submenu) {
        submenu.classList.toggle("show");
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const macroGuia = document.getElementById("macroGuia");
  const path = window.location.pathname;

  const isHome =
    path === "/" || path === "/home/" || path === "{% url 'logistica:index' %}";

  if (isHome) {
    sessionStorage.removeItem("macroGuia");
    macroGuia.innerHTML = "";
    return;
  }

  const rotasMap = [
    { regex: /^\/consulta-id(\/.*)?$/, macro: ["Transporte", "Entrada-Fulfillment", "Consulta ID"] },
    { regex: /^\/pre-recebimento\/?$/, macro: ["Transporte", "Entrada-Fulfillment", "Pré-Recebimento"] },
    { regex: /^\/recebimento\/?$/, macro: ["Transporte", "Entrada-Fulfillment", "Recebimento"] },
    { regex: /^\/consulta\/resultados\/[^/]+\/?$/, macro: ["Transporte", "Entrada-Fulfillment", "Consulta Resultados"] },
    { regex: /^\/estorno\/?$/, macro: ["Transporte", "Entrada-Fulfillment", "Estornos"] },
    { regex: /^\/saida-campo\/?$/, macro: ["Logística", "Saída para Campo", "Saída"] },
    { regex: /^\/consulta-ec\/[^/]+\/?$/, macro: ["Logística", "Saída para Campo", "Consulta Saída"] },
    { regex: /^\/reserva-equip\/?$/, macro: ["Logística", "Reserva de equipamento", "Reserva"] },
    { regex: /^\/consulta-ma\/[^/]+\/?$/, macro: ["Logística", "Reserva de equipamento", "Consulta Reserva"] },
    { regex: /^\/estorno\/reserva-equip\/?$/, macro: ["Logística", "Estornos", "Estorno Reserva de Equipamento"] },
    { regex: /^\/cancelamento\/saida-campo\/?$/, macro: ["Logística", "Estornos", "Estorno Saída para Campo"] }
  ];

  const rotaAtual = rotasMap.find(r => r.regex.test(path));
  if (rotaAtual) {
    const html = rotaAtual.macro.map((parte, index) => {
      return index < rotaAtual.macro.length - 1
        ? `<span>${parte}</span><span>›</span>`
        : `<span>${parte}</span>`;
    }).join("");

    macroGuia.innerHTML = html;
    sessionStorage.setItem("macroGuia", html);
  } else {
    const macroSalva = sessionStorage.getItem("macroGuia");
    if (macroSalva && !macroSalva.includes("Home")) {
      macroGuia.innerHTML = macroSalva;
    } else {
      macroGuia.innerHTML = "";
      sessionStorage.removeItem("macroGuia");
    }
  }

  // Submenus
  document.querySelectorAll(".sub-submenu a").forEach(link => {
    link.addEventListener("click", () => {
      const submenu = link.closest(".sub-submenu");
      const submenuTitle = submenu.previousElementSibling?.textContent?.trim();
      const dropdown = link.closest(".dropdown");
      const dropbtn = dropdown.querySelector(".dropbtn .texto-item")?.textContent?.trim();
      const linkText = link.textContent.trim();

      const partes = [dropbtn, submenuTitle, linkText].filter(Boolean);
      if (partes.length <= 1 || partes.includes("Home")) {
        sessionStorage.removeItem("macroGuia");
        macroGuia.innerHTML = "";
        return;
      }

      const html = partes.map((parte, index) => {
        return index < partes.length - 1
          ? `<span>${parte}</span><span>›</span>`
          : `<span>${parte}</span>`;
      }).join("");

      sessionStorage.setItem("macroGuia", html);
    });
  });

  // Links diretos (sem submenu)
  document.querySelectorAll(".dropdown-content > a").forEach(link => {
    link.addEventListener("click", () => {
      const dropdown = link.closest(".dropdown");
      const dropbtn = dropdown.querySelector(".dropbtn .texto-item")?.textContent?.trim();
      const linkText = link.textContent.trim();

      const partes = [dropbtn, linkText].filter(Boolean);
      if (partes.length <= 1 || partes.includes("Home")) {
        sessionStorage.removeItem("macroGuia");
        macroGuia.innerHTML = "";
        return;
      }

      const html = partes.map((parte, index) => {
        return index < partes.length - 1
          ? `<span>${parte}</span><span>›</span>`
          : `<span>${parte}</span>`;
      }).join("");

      sessionStorage.setItem("macroGuia", html);
    });
  });
});

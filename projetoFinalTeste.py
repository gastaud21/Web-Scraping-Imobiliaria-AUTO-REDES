import requests
import json
import math
from datetime import datetime
import os

"""
Página de exemplo para fazer a busca
https://www.planoaimoveis.com.br/aluguel/?&pagina=1
"""

class PlanoAImoveisScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.planoaimoveis.com.br"
        self.api_url = f"{self.base_url}/retornar-imoveis-disponiveis"
        self.arquivo_dados = "imoveis_data.txt"

        # Payload base
        self.base_payload = {
            "finalidade": "aluguel",
            "codigounidade": "",
            "codigocondominio": "0",
            "codigoproprietario": "0",
            "codigocaptador": "0",
            "codigosimovei": "0",
            "codigocidade": "0",
            "codigoregiao": "0",
            "bairros[0][cidade]": "",
            "bairros[0][codigo]": "",
            "bairros[0][estado]": "",
            "bairros[0][estadoUrl]": "",
            "bairros[0][nome]": "Todos",
            "bairros[0][nomeUrl]": "todos-os-bairros",
            "bairros[0][regiao]": "",
            "endereco": "",
            "edificio": "",
            "numeroquartos": "0",
            "numerovagas": "0",
            "numerobanhos": "0",
            "numerosuite": "0",
            "numerovaranda": "0",
            "numeroelevador": "0",
            "valorde": "0",
            "valorate": "0",
            "areade": "0",
            "areaate": "0",
            "areaexternade": "0",
            "areaexternaate": "0",
            "extras": "",
            "destaque": "0",
            "opcaoimovel[codigo]": "0",
            "opcaoimovel[nome]": "",
            "opcaoimovel[nomeUrl]": "todas-as-opcoes",
            "codigoOpcaoimovel": "0",
            "numeropagina": "1",
            "numeroregistros": "20",
            "ordenacao": "dataatualizacaodesc",
            "condominio[codigo]": "0",
            "condominio[nome]": "",
            "condominio[nomeUrl]": "todos-os-condominios"
        }

        # Inicializar sessão visitando a página
        self._inicializar_sessao()

    def _inicializar_sessao(self):
        """Visita a página inicial para obter cookies de sessão"""
        try:
            print("Inicializando sessão...")
            response = self.session.get(
                f"{self.base_url}/aluguel/?&pagina=1",
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
            )

            if response.status_code == 200:
                print("✓ Sessão inicializada com sucesso!")
                print(f"✓ Cookies obtidos: {list(self.session.cookies.keys())}")
            else:
                print(f"⚠ Aviso: Status {response.status_code} ao inicializar sessão")

        except Exception as e:
            print(f"⚠ Erro ao inicializar sessão: {e}")

    def _get_headers(self, pagina=1):
        """Retorna headers com referer atualizado para a página"""
        return {
            "accept": "*/*",
            "accept-language": "pt-BR,pt;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": self.base_url,
            "referer": f"{self.base_url}/aluguel/?&pagina={pagina}",
            "sec-ch-ua": '"Chromium";v="141", "Not A(Brand";v="8"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

    def buscar_imoveis(self, pagina=1, num_registros=20, filtros=None):
        """
        Busca imóveis de uma página específica

        Args:
            pagina: Número da página (padrão: 1)
            num_registros: Quantidade de registros por página (padrão: 20)
            filtros: Dicionário com filtros adicionais (opcional)

        Returns:
            dict: Dados dos imóveis ou None em caso de erro
        """
        payload = self.base_payload.copy()
        payload["numeropagina"] = str(pagina)
        payload["numeroregistros"] = str(num_registros)

        # Aplicar filtros personalizados
        if filtros:
            payload.update(filtros)

        try:
            response = self.session.post(
                self.api_url,
                headers=self._get_headers(pagina),
                data=payload,
                timeout=30
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except json.JSONDecodeError:
                    print(f"⚠ Resposta não é JSON válido na página {pagina}")
                    return None
            else:
                print(f"✗ Erro na requisição página {pagina}. Status: {response.status_code}")
                return None

        except requests.Timeout:
            print(f"✗ Timeout na requisição página {pagina}")
            return None
        except Exception as e:
            print(f"✗ Erro ao fazer requisição página {pagina}: {e}")
            return None

    def buscar_todos_imoveis(self, filtros=None):
        """
        Busca todos os imóveis disponíveis, fazendo paginação automática

        Args:
            filtros: Dicionário com filtros opcionais

        Returns:
            list: Lista com todos os imóveis encontrados
        """
        print("\n" + "=" * 60)
        print("BUSCANDO TODOS OS IMÓVEIS")
        print("=" * 60)

        # Buscar primeira página para saber o total
        print("\n🔍 Buscando página 1 para calcular total...")
        primeira_pagina = self.buscar_imoveis(pagina=1, filtros=filtros)

        if not primeira_pagina:
            print("✗ Erro ao buscar primeira página")
            return []

        quantidade_total = primeira_pagina.get('quantidade', 0)
        imoveis_por_pagina = 20
        total_paginas = math.ceil(quantidade_total / imoveis_por_pagina)

        print(f"\n📊 Estatísticas:")
        print(f"   • Total de imóveis: {quantidade_total}")
        print(f"   • Imóveis por página: {imoveis_por_pagina}")
        print(f"   • Total de páginas: {total_paginas}")

        # Coletar todos os imóveis
        todos_imoveis = []
        todos_imoveis.extend(primeira_pagina.get('lista', []))

        print(f"\n✓ Página 1/{total_paginas} - {len(primeira_pagina.get('lista', []))} imóveis")

        # Buscar páginas restantes
        for pagina in range(2, total_paginas + 1):
            resultado = self.buscar_imoveis(pagina=pagina, filtros=filtros)

            if resultado and 'lista' in resultado:
                imoveis_pagina = resultado.get('lista', [])
                todos_imoveis.extend(imoveis_pagina)
                print(f"✓ Página {pagina}/{total_paginas} - {len(imoveis_pagina)} imóveis")
            else:
                print(f"⚠ Falha ao buscar página {pagina}")

        print(f"\n✅ Total coletado: {len(todos_imoveis)} imóveis")
        return todos_imoveis

    def salvar_dados(self, imoveis):
        """
        Salva os dados dos imóveis em arquivo JSON

        Args:
            imoveis: Lista de imóveis para salvar
        """
        try:
            dados = {
                "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_imoveis": len(imoveis),
                "imoveis": imoveis
            }

            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)

            print(f"\n💾 Dados salvos em '{self.arquivo_dados}'")
            return True
        except Exception as e:
            print(f"\n✗ Erro ao salvar dados: {e}")
            return False

    def carregar_dados_anteriores(self):
        """
        Carrega dados anteriores do arquivo

        Returns:
            dict: Dados anteriores ou None se não existir
        """
        if not os.path.exists(self.arquivo_dados):
            print(f"\n📄 Arquivo '{self.arquivo_dados}' não encontrado. Primeira execução.")
            return None

        try:
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                dados = json.load(f)

            print(f"\n📂 Dados anteriores carregados:")
            print(f"   • Data da coleta: {dados.get('data_coleta')}")
            print(f"   • Total de imóveis: {dados.get('total_imoveis')}")
            return dados
        except Exception as e:
            print(f"\n✗ Erro ao carregar dados anteriores: {e}")
            return None

    def comparar_dados(self, imoveis_novos):
        """
        Compara imóveis novos com dados anteriores

        Args:
            imoveis_novos: Lista de imóveis da nova coleta
        """
        dados_anteriores = self.carregar_dados_anteriores()

        if not dados_anteriores:
            print("\n✨ Primeira coleta - sem comparação disponível")
            return

        imoveis_antigos = dados_anteriores.get('imoveis', [])

        # Criar sets de códigos para comparação
        codigos_antigos = {str(im.get('codigo')) for im in imoveis_antigos}
        codigos_novos = {str(im.get('codigo')) for im in imoveis_novos}

        # Identificar mudanças
        novos = codigos_novos - codigos_antigos
        removidos = codigos_antigos - codigos_novos
        mantidos = codigos_antigos & codigos_novos

        print("\n" + "=" * 60)
        print("📊 COMPARAÇÃO COM DADOS ANTERIORES")
        print("=" * 60)
        print(f"   • Imóveis mantidos: {len(mantidos)}")
        print(f"   • Imóveis NOVOS: {len(novos)}")
        print(f"   • Imóveis REMOVIDOS: {len(removidos)}")

        # Mostrar detalhes dos novos
        if novos:
            print(f"\n🆕 NOVOS IMÓVEIS ({len(novos)}):")
            for codigo in list(novos)[:5]:  # Mostrar até 5
                imovel = next((im for im in imoveis_novos if str(im.get('codigo')) == codigo), None)
                if imovel:
                    print(f"   • Código {codigo}: {imovel.get('titulo', 'N/A')[:80]}...")
            if len(novos) > 5:
                print(f"   ... e mais {len(novos) - 5} novos imóveis")

        # Mostrar detalhes dos removidos
        if removidos:
            print(f"\n🗑️  IMÓVEIS REMOVIDOS ({len(removidos)}):")
            for codigo in list(removidos)[:5]:  # Mostrar até 5
                imovel = next((im for im in imoveis_antigos if str(im.get('codigo')) == codigo), None)
                if imovel:
                    print(f"   • Código {codigo}: {imovel.get('titulo', 'N/A')[:80]}...")
            if len(removidos) > 5:
                print(f"   ... e mais {len(removidos) - 5} imóveis removidos")


# ===== EXEMPLO DE USO =====

# Criar instância do scraper
scraper = PlanoAImoveisScraper()

# Buscar todos os imóveis
imoveis = scraper.buscar_todos_imoveis()

# Comparar com dados anteriores
if imoveis:
    scraper.comparar_dados(imoveis)

    # Salvar novos dados
    scraper.salvar_dados(imoveis)

    print("\n✅ Processo concluído com sucesso!")
else:
    print("\n✗ Nenhum imóvel foi coletado")

# ===== EXEMPLO COM FILTROS =====
# Descomente para buscar com filtros específicos

# print("\n" + "="*60)
# print("BUSCA COM FILTROS")
# print("="*60)
#
# imoveis_filtrados = scraper.buscar_todos_imoveis(
#     filtros={
#         "numeroquartos": "2",
#         "numerovagas": "1"
#     }
# )
#
# if imoveis_filtrados:
#     print(f"\n✓ Total de imóveis filtrados: {len(imoveis_filtrados)}")
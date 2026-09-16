import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).with_name("estudos.db")

DADOS = {
    "Geral": [
        "Direito Constitucional -> art 1 ao 5",
        "Direito Constitucional -> 6 ao 17",
        "Estatuto GCM Federal",
        "Lei Orgânica Municipal de Toledo",
        "Estatuto do Desarmamento",
        "Maria da Penha",
        "Lei de Drogas",
    ],

    "Direito Penal": [
        "Título I: Da aplicação da lei penal",
        "Título II: Do crime",
        "Título III: Da imputabilidade penal",
        "Título IV: Do concurso de pessoas",
        "Título V: Das penas",
        "Título VI: Das medidas de segurança",
        "Título VII: Da ação penal",
        "Título VIII: Da extinção da punibilidade",
        "Título I: Dos crimes contra a pessoa",
        "Título II: Dos crimes contra o patrimônio",
        "Título III: Dos crimes contra a propriedade imaterial",
        "Título IV: Dos crimes contra a organização do trabalho",
        "Título V: Dos crimes contra o sentimento religioso e contra o respeito aos mortos",
        "Título VI: Dos crimes contra a dignidade sexual",
        "Título VII: Dos crimes contra a família",
        "Título VIII: Dos crimes contra a incolumidade pública",
        "Título IX: Dos crimes contra a paz pública",
        "Título X: Dos crimes contra a fé pública",
        "Título XI: Dos crimes contra a administração pública",
    ],

    "Direito Administrativo": [
        "Regime Jurídico Administrativo",
        "Conceito de Direito Administrativo e Administração Pública",
        "Organização da Administração Pública",
        "Terceiro Setor e Entidades Paraestatais",
        "Competências Administrativas e Poderes Administrativos",
        "Atos Administrativos",
        "Licitações na Lei nº 14.133/2021",
        "Contratos Administrativos na Lei nº 14.133/2021",
        "Serviços Públicos",
        "Concessão, permissão e autorização de Serviços Públicos",
        "Agentes Públicos",
        "Regime jurídico disciplinar dos Agentes Públicos",
        "Controle da Administração Pública",
        "Improbidade Administrativa",
        "Lei anticorrupção (Lei 12.846/2013)",
        "Responsabilidade civil do Estado",
        "Bens Públicos",
        "Intervenção do Estado na propriedade privada",
    ],

    "CTB": [
        "Capítulo I: Disposições Preliminares",
        "Capítulo II: Do Sistema Nacional de Trânsito",
        "Capítulo III: Das Normas Gerais de Circulação e Conduta",
        "Capítulo III-A: Da Condução de Veículos por Motoristas Profissionais",
        "Capítulo IV: Dos Pedestres e Condutores de Veículos não Motorizados",
        "Capítulo V: Do Cidadão",
        "Capítulo VI: Da Educação para o Trânsito",
        "Capítulo VII: Da Sinalização de Trânsito",
        "Capítulo VIII: Da Engenharia de Tráfego, da Operação, da Fiscalização e do Policiamento Ostensivo de Trânsito",
        "Capítulo IX: Dos Veículos",
        "Capítulo X: Dos Veículos em Circulação Internacional",
        "Capítulo XI: Do Registro de Veículos",
        "Capítulo XII: Do Licenciamento",
        "Capítulo XIII: Da Condução de Escolares",
        "Capítulo XIII-A: Da Condução de Moto-Frete",
        "Capítulo XIV: Da Habilitação",
        "Capítulo XV: Das Infrações",
        "Capítulo XVI: Das Penalidades",
        "Capítulo XVII: Das Medidas Administrativas",
        "Capítulo XVIII: Do Processo Administrativo",
        "Capítulo XIX: Dos Crimes de Trânsito",
        "Capítulo XX: Disposições Finais e Transitórias",
    ],

    "Português": [
        "Hífen",
    ],

    "Matemática": [],

    "Informática": [
        "Aula 00", "Aula 01", "Aula 02", "Aula 03",
        "Aula 04", "Aula 05", "Aula 06", "Aula 07",
        "Aula 08", "Aula 09", "Aula 10", "Aula 11",
        "Aula 12", "Aula 13", "Aula 14", "Aula 15",
        "Aula 16", "Aula 17", "Aula 18", "Aula 19",
        "Aula 20", "Aula 21", "Aula 22", "Aula 23",
        "Aula 24", "Aula 25", "Aula 26", "Aula 27",
        "Aula 28", "Aula 29", "Aula 30", "Aula 31",
    ],
}


def main():
    if not CAMINHO_BANCO.exists():
        print("ERRO: estudos.db não foi encontrado na mesma pasta deste arquivo.")
        print("Coloque importar_topicos.py dentro de C:\\SistemaEstudos.")
        return

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")

    inseridos = 0
    existentes = 0

    try:
        for disciplina, topicos in DADOS.items():
            conexao.execute(
                "INSERT OR IGNORE INTO disciplinas (nome) VALUES (?)",
                (disciplina,)
            )

            disciplina_id = conexao.execute(
                "SELECT id FROM disciplinas WHERE nome = ?",
                (disciplina,)
            ).fetchone()[0]

            for topico in topicos:
                cursor = conexao.execute(
                    """
                    INSERT OR IGNORE INTO topicos (disciplina_id, nome)
                    VALUES (?, ?)
                    """,
                    (disciplina_id, topico)
                )

                if cursor.rowcount == 1:
                    inseridos += 1
                else:
                    existentes += 1

        conexao.commit()

    finally:
        conexao.close()

    print()
    print("IMPORTAÇÃO CONCLUÍDA")
    print("--------------------")
    print(f"Tópicos novos: {inseridos}")
    print(f"Já existentes: {existentes}")
    print()
    print("Nenhuma revisão ou histórico foi apagado.")
    print("Agora abra o programa novamente com: python main.py")


if __name__ == "__main__":
    main()

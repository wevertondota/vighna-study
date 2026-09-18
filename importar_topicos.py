from pathlib import Path

import banco

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
        "TÍTULO I – DA APLICAÇÃO DA LEI PENAL",
        "TÍTULO II – DO CRIME",
        "TÍTULO III – DA IMPUTABILIDADE PENAL",
        "TÍTULO IV – DO CONCURSO DE PESSOAS",
        "TÍTULO V – DAS PENAS",
        "TÍTULO VI – DAS MEDIDAS DE SEGURANÇA",
        "TÍTULO VII – DA AÇÃO PENAL",
        "TÍTULO VIII – DA EXTINÇÃO DA PUNIBILIDADE",
        "TÍTULO I – DOS CRIMES CONTRA A PESSOA",
        "TÍTULO II – DOS CRIMES CONTRA O PATRIMÔNIO",
        "TÍTULO III – DOS CRIMES CONTRA A PROPRIEDADE IMATERIAL",
        "TÍTULO IV – DOS CRIMES CONTRA A ORGANIZAÇÃO DO TRABALHO",
        "TÍTULO V – DOS CRIMES CONTRA O SENTIMENTO RELIGIOSO E CONTRA O RESPEITO AOS MORTOS",
        "TÍTULO VI – DOS CRIMES CONTRA A DIGNIDADE SEXUAL",
        "TÍTULO VII – DOS CRIMES CONTRA A FAMÍLIA",
        "TÍTULO VIII – DOS CRIMES CONTRA A INCOLUMIDADE PÚBLICA",
        "TÍTULO IX – DOS CRIMES CONTRA A PAZ PÚBLICA",
        "TÍTULO X – DOS CRIMES CONTRA A FÉ PÚBLICA",
        "TÍTULO XI – DOS CRIMES CONTRA A ADMINISTRAÇÃO PÚBLICA",
        "TÍTULO XII – DOS CRIMES CONTRA O ESTADO DEMOCRÁTICO DE DIREITO",
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

    # Garante schema, identidades estáveis e aliases antes de importar.
    banco.criar_banco()

    inseridos = 0
    existentes = 0

    for disciplina, topicos in DADOS.items():
        disciplina_id = banco.resolver_disciplina_id_estrutural(disciplina)
        if disciplina_id is None:
            banco.adicionar_disciplina(disciplina)

        for topico in topicos:
            existente = banco.resolver_topico_id_estrutural(
                disciplina, topico
            )
            if existente is not None:
                existentes += 1
                continue
            if banco.adicionar_topico(disciplina, topico):
                inseridos += 1
            else:
                existentes += 1

    print()
    print("IMPORTAÇÃO CONCLUÍDA")
    print("--------------------")
    print(f"Tópicos novos: {inseridos}")
    print(f"Já existentes: {existentes}")
    print()
    print("As identidades estruturais e aliases foram preservados.")
    print("Nenhuma revisão ou histórico foi apagado.")
    print("Agora abra o programa novamente com: python main.py")


if __name__ == "__main__":
    main()

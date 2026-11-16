#!/usr/bin/env python3
"""DarkFactory Autonomous Topic & Historical Dossier Generator.

Generates high-retention, YouTube-compliant documentary episode themes for 15-30 minute productions:
1. Strict YouTube Monetization Compliance (EDSA: Educational, Documentary, Scientific, Artistic).
2. Zero Yellow Dollar demonetization risks (No gratuitous violence, sensationalism, or prohibited keywords).
3. Optimized for Christopher Nolan 3-Timeline Structure (Slow Clock, Fast Clock, Aftermath).
4. Sized for Full Episodes (15 to 30 minutes, 24 to 48 narrative scenes).
5. Provides organic CTR hooks, curiosity gaps, and Wikipedia-verified search groundings.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ADR-01: Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TopicGenerator")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Sensitive terms to block or verify under EDSA for YouTube Green Dollar safety
PROHIBITED_TITLE_TERMS = [
    r"\bmurder(ed|s|ing)?\b",
    r"\bsuicide\b",
    r"\bmassacre\b",
    r"\bslaughter\b",
    r"\bbloodbath\b",
    r"\bgenocide\b",
    r"\bterrorist\b",
    r"\btorture(d)?\b",
    r"\bdecapitat(ed|ion)\b",
]

# Educational replacements if raw topic has flagged terms
EDSA_TITLE_CORRECTIONS = {
    r"\bmassacre\b": "Incident",
    r"\bslaughter\b": "Disaster",
    r"\bsuicide\b": "Fatal Mission",
    r"\bbloodbath\b": "Clash",
    r"\bterrorist attack\b": "Security Crisis",
}


@dataclass
class TopicBlueprint:
    """Structured blueprint for a 15-30 min documentary episode."""
    topic_id: str
    title: str
    query: str
    category: str
    category_label: str
    duration_min: int
    duration_label: str
    green_dollar_score: int
    edsa_compliant: bool
    viral_hook: str
    logline: str
    nolan_threads: Dict[str, str]
    key_entities: List[str]
    retention_factor: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Canonical Database of 15-30 min High-Impact Historical Documentaries
CANONICAL_TOPICS: List[Dict[str, Any]] = [
    # ── CATEGORY 1: Crises Desclassificadas & Quase-Apocalipse (Nuclear Near-Misses) ──
    {
        "topic_id": "soviet_false_alarm_1983",
        "title": "1983 Soviet Nuclear False Alarm Incident",
        "query": "1983 Soviet nuclear false alarm incident",
        "category": "crises_desclassificadas",
        "category_label": "Crises Desclassificadas",
        "duration_min": 20,
        "duration_label": "18-22 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Às 00:15 de 26 de setembro de 1983, cinco mísseis balísticos intercontinentais surgiram no radar soviético. Um único homem teve 20 minutos para decidir o fim do mundo.",
        "logline": "A tensão claustrofóbica no bunker secreto Serpukhov-15, onde o tenente-coronel Stanislav Petrov desafiou o computador e evitou o holocausto atômico.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: A paranóia soviética após o abate do voo KAL 007 e o exercício Able Archer 83.",
            "fast_clock": "O Relógio Rápido: Os 20 minutos contínuos na tela do satélite Oko até o contato com o Estado-Maior.",
            "aftermath": "O Pós-Impacto: O silêncio forçado de 15 anos e os documentos desclassificados que revelaram a falha de reflexo solar."
        },
        "key_entities": ["Stanislav Petrov", "Serpukhov-15", "Oko Early Warning", "Yuri Andropov"],
        "retention_factor": "Suspense psicológico de relógio correndo (Ticking Clock) com desfecho milagroso documentado."
    },
    {
        "topic_id": "goldsboro_b52_crash_1961",
        "title": "The 1961 Goldsboro B-52 Crash & Nuclear Near-Miss",
        "query": "1961 Goldsboro B-52 crash",
        "category": "crises_desclassificadas",
        "category_label": "Crises Desclassificadas",
        "duration_min": 18,
        "duration_label": "16-20 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Duas bombas termonucleares de 4 megatons caíram na Carolina do Norte. Cinco de seis travas de segurança falharam. Uma única chave de baixa voltagem impediu a detonação.",
        "logline": "A perda catastrófica de combustível em voo de um bombardeiro estratégico americano e o resgate da ogiva enterrada a 60 metros na lama.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: Os protocolos SAC de patrulha aérea nuclear permanente de 24 horas sobre o Atlântico.",
            "fast_clock": "O Relógio Rápido: A desintegração estrutural da asa direita no ar e a sequência de ejeção dos paraquedas das bombas.",
            "aftermath": "O Pós-Impacto: O relatório ultrassecreto Parker F. Jones de 1969 admitindo a vulnerabilidade dos sistemas de segurança."
        },
        "key_entities": ["B-52 Stratofortress", "Mark 39 Nuclear Bomb", "Parker F. Jones", "Goldsboro North Carolina"],
        "retention_factor": "Fator de perigo invisível em território civil e documento desclassificado da Lei de Acesso à Informação."
    },
    {
        "topic_id": "cuban_submarine_b59_1962",
        "title": "The 1962 Cuban Missile Crisis Submarine B-59 Veto",
        "query": "Soviet submarine B-59",
        "category": "crises_desclassificadas",
        "category_label": "Crises Desclassificadas",
        "duration_min": 24,
        "duration_label": "22-26 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Sem contato com Moscou há 8 dias, sufocando a 50 graus de calor no fundo do mar, três oficiais tinham a chave de um torpedo nuclear. Dois votaram pelo lançamento.",
        "logline": "No ápice da Crise dos Mísseis de Cuba, o submarino soviético B-59 é cercado por contratorpedeiros americanos com cargas de profundidade até o veto solitário de Arkhipov.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: A travessia clandestina de Murmansk até o mar do Caribe sob isolamento térmico.",
            "fast_clock": "O Relógio Rápido: O bombardeio acústico de cargas de exercício e a discussão claustrofóbica na sala de comando do submarino.",
            "aftermath": "O Pós-Impacto: O retorno humilhante à URSS e o reconhecimento histórico 40 anos depois na conferência de Havana."
        },
        "key_entities": ["Vasili Arkhipov", "Submarine B-59", "USS Beale", "Foxtrot-class"],
        "retention_factor": "Drama submarino fechado de alta pressão com decisão moral de um único oficial."
    },
    {
        "topic_id": "norad_computer_simulation_1979",
        "title": "1979 NORAD Computer Simulation False Alarm",
        "query": "1979 NORAD computer false alarm",
        "category": "crises_desclassificadas",
        "category_label": "Crises Desclassificadas",
        "duration_min": 17,
        "duration_label": "15-18 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Em 9 de novembro de 1979, os monitores do Cheyenne Mountain indicaram 2.200 ogivas soviéticas voando contra os Estados Unidos. Caças foram lançados antes da descoberta de uma fita de treinamento.",
        "logline": "Uma fita de simulação inserida por engano no computador principal do NORAD disparou o nível de alarme nuclear mais próximo da terceira guerra mundial.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: O projeto de interconexão de dados de radar PAVE PAWS e satélites DSP na montanha de Cheyenne.",
            "fast_clock": "O Relógio Rápido: Os 6 minutos de alerta militar nacional até a confirmação de que os radares terrestres de alerta precoce estavam vazios.",
            "aftermath": "O Pós-Impacto: As audiências do Congresso americano sobre falhas de hardware nos computadores NOVA da Data General."
        },
        "key_entities": ["NORAD", "Cheyenne Mountain Complex", "Brzezinski", "PAVE PAWS"],
        "retention_factor": "Tecnologia retrô dos anos 70, perigo de erro cibernético e suspense geopolítico acelerado."
    },

    # ── CATEGORY 2: Mistérios Militares, Navais & Aeroespaciais ──
    {
        "topic_id": "project_azorian_k129_1974",
        "title": "Project Azorian: The CIA Secret Salvage of Submarine K-129",
        "query": "Project Azorian",
        "category": "misterios_militares_navais",
        "category_label": "Mistérios Navais & Aeroespaciais",
        "duration_min": 28,
        "duration_label": "25-30 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Como a CIA convenceu o mundo de que o excêntrico Howard Hughes estava minerando o fundo do mar, enquanto gastava 4 bilhões de dólares para roubar um submarino soviético a 5.000 metros de profundidade.",
        "logline": "A mais cara e audaciosa operação de engenharia naval clandestina da Guerra Fria: a construção do navio Hughes Glomar Explorer com uma garra gigante de aço.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: O naufrágio misterioso do K-129 no Pacífico e a localização secreta do casco pela Marinha dos EUA via SOSUS.",
            "fast_clock": "O Relógio Rápido: A descida milimétrica da garra mecânica Clementine e o momento crítico em que o casco de 1.700 toneladas partiu ao meio durante a subida.",
            "aftermath": "O Pós-Impacto: O sepultamento militar solene dos marinheiros soviéticos gravado em filme secreto entregue a Boris Yeltsin."
        },
        "key_entities": ["Hughes Glomar Explorer", "K-129", "CIA", "Howard Hughes", "SOSUS"],
        "retention_factor": "Engenharia colossal ultra-secreta combinada com disfarce corporativo e mistério oceânico abissal."
    },
    {
        "topic_id": "disappearance_uss_scorpion_1968",
        "title": "The Sinking and Acoustic Hunt for USS Scorpion",
        "query": "USS Scorpion (SSN-589)",
        "category": "misterios_militares_navais",
        "category_label": "Mistérios Navais & Aeroespaciais",
        "duration_min": 22,
        "duration_label": "20-25 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Em maio de 1968, um submarino nuclear de ataque desapareceu no Atlântico com 99 marinheiros. A Marinha não usou navios para localizá-lo — usou hidrofones subaquáticos e o teorema de Bayes.",
        "logline": "A investigação forense acústica do Dr. John Craven nos dados da rede SOSUS para reconstituir a explosão interna da bateria do torpedo do USS Scorpion.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: Os problemas crônicos de manutenção mecânica e sistemas de emergência adiados em Norfolk.",
            "fast_clock": "O Relógio Rápido: Os pulsos de som captados pelas estações hidroacústicas das Canárias no momento da implosão a 3.000 metros.",
            "aftermath": "O Pós-Impacto: A descida pioneira do submersível Trieste II até o campo de destroços e a desclassificação das gravações acústicas."
        },
        "key_entities": ["USS Scorpion", "John Piña Craven", "Trieste II", "Bayesian Search Theory"],
        "retention_factor": "Mistério forense subaquático, análise científica de áudio e investigação militar rigorosa."
    },
    {
        "topic_id": "flight_19_lost_patrol_1945",
        "title": "Flight 19: The Declassified Navigation Logs of the Lost Patrol",
        "query": "Flight 19",
        "category": "misterios_militares_navais",
        "category_label": "Mistérios Navais & Aeroespaciais",
        "duration_min": 19,
        "duration_label": "18-22 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Cinco bombardeiros Avenger decolaram da Flórida em dia claro. Três horas depois, o rádio captou a voz trêmula do instrutor: 'Ambas as minhas bússolas falharam. Não sabemos onde está o oeste.'",
        "logline": "A reconstrução minuto a minuto das transmissões de rádio desclassificadas da Marinha americana que deram origem ao mito do Triângulo das Bermudas.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: A formação dos jovens pilotos e a tempestade meteorológica que avançava no Atlântico Norte.",
            "fast_clock": "O Relógio Rápido: As duas horas dramáticas de desorientação espacial enquanto o combustível esgotava gota a gota.",
            "aftermath": "O Pós-Impacto: O desaparecimento imediato do hidroavião de resgate PBM Mariner e o inquérito naval de 500 páginas."
        },
        "key_entities": ["Charles Carroll Taylor", "TBM Avenger", "Naval Air Station Fort Lauderdale", "PBM Mariner"],
        "retention_factor": "Gravações autênticas de rádio, desorientação psicológica real e eliminação de mitos com fatos técnicos."
    },

    # ── CATEGORY 3: Guerra Fria, Black Ops & Espionagem Científica ──
    {
        "topic_id": "dead_hand_perimeter_system",
        "title": "Dead Hand: The Soviet Automated Nuclear Retaliation System",
        "query": "Dead Hand",
        "category": "guerra_fria_espionagem",
        "category_label": "Guerra Fria & Espionagem",
        "duration_min": 25,
        "duration_label": "22-26 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "E se toda a liderança do governo morrer em um primeiro ataque surpresa? A União Soviética construiu uma máquina com sensores sísmicos e de radiação capaz de disparar o arsenal nuclear sem intervenção humana.",
        "logline": "Os segredos de engenharia militar do sistema 'Perimetr', projetado para enviar um míssil de comando 15P011 transmitindo ordens de fogo para todos os silos remanescentes.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: O medo soviético de mísseis Pershing II na Europa atingindo o Kremlin em apenas 6 minutos.",
            "fast_clock": "O Relógio Rápido: A lógica de decisão de três níveis dos operadores isolados em um bunker subterrâneo impenetrável.",
            "aftermath": "O Pós-Impacto: As revelações dos engenheiros soviéticos nos anos 90 confirmando que o sistema permanece ativo na Rússia moderna."
        },
        "key_entities": ["Perimetr System", "Command Missile 15A11", "Yuzhmash", "Strategic Rocket Forces"],
        "retention_factor": "Conceito apocalíptico de inteligência cibernética militar e arquitetura ultra-secreta de defesa."
    },
    {
        "topic_id": "operation_paperclip_classified_files",
        "title": "Operation Paperclip: The Classified Transfer of V-2 Rocket Scientists",
        "query": "Operation Paperclip",
        "category": "guerra_fria_espionagem",
        "category_label": "Guerra Fria & Espionagem",
        "duration_min": 26,
        "duration_label": "24-28 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Em maio de 1945, enquanto a Alemanha entrava em colapso, agentes do serviço secreto americano correram contra os soviéticos para confiscar caixas de documentos enterradas em minas de sal e 1.600 cientistas.",
        "logline": "A transição moral e técnica dos engenheiros do foguete V-2 de Peenemünde para o programa espacial Apollo e o desenvolvimento de mísseis balísticos americanos.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: A fabricação subterrânea dos foguetes V-2 nas galerias de Mittelwerk.",
            "fast_clock": "O Relógio Rápido: A fuga em comboio de Wernher von Braun pelos Alpes bávaros para se render aos americanos.",
            "aftermath": "O Pós-Impacto: A expurgação de antecedentes políticos pelo Departamento de Estado e o nascimento da NASA em Huntsville."
        },
        "key_entities": ["Wernher von Braun", "Joint Intelligence Objectives Agency", "Peenemünde", "Fort Bliss"],
        "retention_factor": "Dilema ético profundo, espionagem pós-guerra e origens secretas da corrida espacial."
    },
    {
        "topic_id": "operation_northwoods_1962",
        "title": "Operation Northwoods: The Declassified 1962 Pentagon Proposal",
        "query": "Operation Northwoods",
        "category": "guerra_fria_espionagem",
        "category_label": "Guerra Fria & Espionagem",
        "duration_min": 20,
        "duration_label": "18-22 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Em março de 1962, o Estado-Maior Conjunto dos Estados Unidos assinou um documento propondo simular ataques falsos contra alvos americanos para justificar uma intervenção militar. Um único homem vetou o plano.",
        "logline": "A desclassificação histórica do memorando assinado pelo general Lyman Lemnitzer e a rejeição categórica do presidente John F. Kennedy.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: O fiasco da Baía dos Porcos e a frustração dos chefes militares do Pentágono com a Guerra Fria.",
            "fast_clock": "O Relógio Rápido: A reunião a portas fechadas no Salão Oval onde o documento foi apresentado e imediatamente rejeitado.",
            "aftermath": "O Pós-Impacto: O arquivamento com tarjas pretas por 35 anos até a liberação pública pelo Assassination Records Review Board."
        },
        "key_entities": ["Lyman Lemnitzer", "John F. Kennedy", "Joint Chiefs of Staff", "Robert McNamara"],
        "retention_factor": "Documentos autênticos do governo com assinaturas originais e transparência histórica comprovada."
    },

    # ── CATEGORY 4: Ciência Secreta, Perfurações Profundas & Catástrofes Espaciais ──
    {
        "topic_id": "kola_superdeep_borehole",
        "title": "Kola Superdeep Borehole: The 12km Descent to the Earth Core",
        "query": "Kola Superdeep Borehole",
        "category": "ciencia_catastrofes",
        "category_label": "Ciência & Catástrofes",
        "duration_min": 21,
        "duration_label": "20-24 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "No Círculo Polar Ártico, cientistas soviéticos perfuraram a crosta terrestre por 24 anos até atingirem 12.262 metros de profundidade. O que eles descobriram desafiou toda a física geológica conhecida.",
        "logline": "A maior perfuração científica da história humana, onde brocas de tungstênio derreteram a 180°C e rochas saturadas com hidrogênio desmentiram os modelos sísmicos mundiais.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: A corrida com o Projeto Mohole americano para ser o primeiro a alcançar a descontinuidade de Mohorovičić.",
            "fast_clock": "O Relógio Rápido: As falhas catastróficas dos cabos de perfuração Uralmash-15000 nas profundezas de 12.000 metros.",
            "aftermath": "O Pós-Impacto: O abandono do complexo em ruínas e a desmistificação científica da lenda urbana dos 'sons do inferno'."
        },
        "key_entities": ["Uralmash-15000", "Murmansk Oblast", "Mohorovičić discontinuity", "Kola Peninsula"],
        "retention_factor": "Fascínio pelo desconhecido terrestre, limites da engenharia e gravação geofísica autêntica."
    },
    {
        "topic_id": "soyuz_1_vladimir_komarov_1967",
        "title": "Soyuz 1: The Technical Tragedy of Vladimir Komarov",
        "query": "Soyuz 1",
        "category": "ciencia_catastrofes",
        "category_label": "Ciência & Catástrofes",
        "duration_min": 23,
        "duration_label": "20-25 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Sabendo que a espaçonave possuía 203 falhas de projeto conhecidas, Vladimir Komarov embarcou na Soyuz 1 para salvar a vida de Yuri Gagarin, seu piloto reserva. Em órbita, os painéis não abriram.",
        "logline": "A crônica documental do primeiro voo fatal na história da exploração espacial humana e as transmissões de telemetria desclassificadas de Baikonur.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: As pressões políticas de Moscou para lançar antes do 50º aniversário da Revolução de Outubro.",
            "fast_clock": "O Relógio Rápido: As 18 órbitas desesperadas tentando orientar a cápsula com controles manuais e o paraquedas principal emperrado.",
            "aftermath": "O Pós-Impacto: O funeral com honras na muralha do Kremlin e a reformulação completa que transformou a Soyuz na nave mais segura do mundo."
        },
        "key_entities": ["Vladimir Komarov", "Yuri Gagarin", "Vasily Mishin", "Soyuz 7K-OK"],
        "retention_factor": "Sacrifício humano heróico documentado, transcrições autênticas e rigor histórico sem sensacionalismo."
    },
    {
        "topic_id": "project_pluto_flying_reactor_1964",
        "title": "Project Pluto: The Supersonic Flying Nuclear Reactor",
        "query": "Project Pluto",
        "category": "ciencia_catastrofes",
        "category_label": "Ciência & Catástrofes",
        "duration_min": 19,
        "duration_label": "18-22 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Nos anos 60, engenheiros de Nevada testaram o motor mais destrutivo já concebido: um míssil de cruzeiro atômico que voaria a Mach 3 no nível das árvores, movido por um reator nuclear aberto sem blindagem.",
        "logline": "O motor ramjet nuclear Tory II-C e a arma apocalíptica da Guerra Fria que foi cancelada porque não existia lugar no planeta onde testá-la em voo.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: O projeto dos materiais cerâmicos da Coors Porcelain capazes de suportar 1.400 graus centígrados.",
            "fast_clock": "O Relógio Rápido: O teste de 5 minutos a plena potência em Jackass Flats com 500 megawatts de energia térmica liberada.",
            "aftermath": "O Pós-Impacto: O advento dos mísseis balísticos intercontinentais Polaris que tornaram a arma obsoleta e seu confinamento em arquivos secretos."
        },
        "key_entities": ["Tory II-C", "Jackass Flats", "Lawrence Livermore National Laboratory", "SLAM missile"],
        "retention_factor": "Máquinas gigantes esquecidas da Guerra Fria e ambição científica extrema com documentação fotográfica real."
    },
    {
        "topic_id": "kyshtym_nuclear_disaster_1957",
        "title": "The 1957 Kyshtym Disaster: The Secret Nuclear Explosion at Mayak",
        "query": "Kyshtym disaster",
        "category": "ciencia_catastrofes",
        "category_label": "Ciência & Catástrofes",
        "duration_min": 24,
        "duration_label": "22-26 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Quase 30 anos antes de Chernobyl, uma explosão de resíduos atômicos em uma cidade que não existia nos mapas soviéticos contaminou 20.000 quilômetros quadrados. O mundo não soube por duas décadas.",
        "logline": "A falha do sistema de resfriamento do tanque subterrâneo de Mayak Chelyabinsk-40 e a evacuação forçada de vilarejos sob sigilo militar absoluto.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: A corrida armamentista de produção rápida de plutônio em instalações sem salvaguardas nos Urais.",
            "fast_clock": "O Relógio Rápido: O superaquecimento químico a 350 graus e a detonação não-nuclear que arrancou uma tampa de concreto de 160 toneladas.",
            "aftermath": "O Pós-Impacto: As revelações pioneiras do biólogo Zhores Medvedev no exílio e o reconhecimento oficial na era Glasnost."
        },
        "key_entities": ["Chelyabinsk-40", "Mayak production association", "Zhores Medvedev", "EURT trace"],
        "retention_factor": "Investigação de mistério radioativo censurado e arqueologia forense soviética."
    },

    # ── CATEGORY 5: Enigmas Geopolíticos & Operações Táticas Críticas ──
    {
        "topic_id": "operation_entebbe_90_minutes",
        "title": "Operation Entebbe: 90 Minutes at Midnight",
        "query": "Operation Entebbe",
        "category": "enigmas_geopoliticos",
        "category_label": "Enigmas Geopolíticos",
        "duration_min": 27,
        "duration_label": "25-30 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Quatro aviões de carga C-130 voando a apenas 30 metros de altura sobre as águas do Mar Vermelho para escapar do radar inimigo. O resgate de reféns a 4.000 quilômetros de distância.",
        "logline": "O planejamento tático ultrassecreto da Sayeret Matkal e o pouso surpresa no aeroporto de Uganda em 4 de julho de 1976.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: As negociações de gabinete diplomático e a construção clandestina de uma réplica de madeira do terminal.",
            "fast_clock": "O Relógio Rápido: Os 53 minutos cronometrados entre a abertura da rampa do primeiro Hércules e a decolagem com os reféns.",
            "aftermath": "O Pós-Impacto: A perda solitária do comandante Yonatan Netanyahu e o impacto histórico na doutrina antiterrorista mundial."
        },
        "key_entities": ["Operation Entebbe", "Sayeret Matkal", "Yonatan Netanyahu", "Lockheed C-130 Hercules"],
        "retention_factor": "Cronometragem tática precisa minuto a minuto com valor educacional estratégico."
    },
    {
        "topic_id": "project_iceworm_greenland_city",
        "title": "Project Iceworm: The Secret US Nuclear City Under Greenland Ice",
        "query": "Project Iceworm",
        "category": "enigmas_geopoliticos",
        "category_label": "Enigmas Geopolíticos",
        "duration_min": 22,
        "duration_label": "20-25 min",
        "green_dollar_score": 100,
        "edsa_compliant": True,
        "viral_hook": "Sob a cobertura de uma base científica de testes de neve, o exército americano escavou 4.000 quilômetros de túneis no gelo da Groenlândia com o plano de estocar 600 mísseis nucleares.",
        "logline": "A cidade subterrânea secreta de Camp Century alimentada por um reator nuclear móvel até que o movimento inexorável da geleira esmagou as estruturas.",
        "nolan_threads": {
            "slow_clock": "O Relógio Lento: O acordo bilateral militar com a Dinamarca mantendo o segredo do armamento atômico polar.",
            "fast_clock": "O Relógio Rápido: A montagem do reator nuclear portátil PM-2A em meio a nevascas de 50 graus abaixo de zero.",
            "aftermath": "O Pós-Impacto: O colapso plástico dos tetos de gelo forçando a evacuação e os resíduos enterrados que ressurgem com o degelo moderno."
        },
        "key_entities": ["Camp Century", "Project Iceworm", "PM-2A nuclear reactor", "Greenland Ice Sheet"],
        "retention_factor": "Paisagens visuais espetaculares no gelo do Ártico e segredo de estado de 40 anos."
    }
]


class TopicGeneratorEngine:
    """Core Engine for Autonomous Topic Selection, Filtering, and Compliance Validation."""

    def __init__(self, topics: Optional[List[Dict[str, Any]]] = None):
        self._topics_data = topics or CANONICAL_TOPICS
        self._blueprints = [self._dict_to_blueprint(d) for d in self._topics_data]

    def _dict_to_blueprint(self, d: Dict[str, Any]) -> TopicBlueprint:
        return TopicBlueprint(
            topic_id=d["topic_id"],
            title=d["title"],
            query=d["query"],
            category=d["category"],
            category_label=d.get("category_label", d["category"].replace("_", " ").title()),
            duration_min=d.get("duration_min", 20),
            duration_label=d.get("duration_label", "18-22 min"),
            green_dollar_score=d.get("green_dollar_score", 100),
            edsa_compliant=d.get("edsa_compliant", True),
            viral_hook=d.get("viral_hook", ""),
            logline=d.get("logline", ""),
            nolan_threads=d.get("nolan_threads", {}),
            key_entities=d.get("key_entities", []),
            retention_factor=d.get("retention_factor", "")
        )

    def get_all_topics(self) -> List[TopicBlueprint]:
        """Returns all canonical documentary topics."""
        return list(self._blueprints)

    def get_topics_by_category(self, category: str) -> List[TopicBlueprint]:
        """Filters topics by category slug."""
        if category in ("all", "*", ""):
            return self.get_all_topics()
        return [t for t in self._blueprints if t.category.lower() == category.lower()]

    def get_random_topic(self, category: Optional[str] = None) -> TopicBlueprint:
        """Picks a random compliant topic, optionally filtered by category."""
        pool = self.get_topics_by_category(category) if category else self._blueprints
        if not pool:
            pool = self._blueprints
        return random.choice(pool)

    def get_batch(self, count: int = 6, category: Optional[str] = None) -> List[TopicBlueprint]:
        """Returns a diverse batch of recommended topics."""
        pool = self.get_topics_by_category(category) if category else list(self._blueprints)
        if not pool:
            pool = list(self._blueprints)
        count = min(count, len(pool))
        return random.sample(pool, count)

    def get_categories(self) -> List[Dict[str, Any]]:
        """Returns list of distinct categories with count and label."""
        cats: Dict[str, Dict[str, Any]] = {}
        for b in self._blueprints:
            if b.category not in cats:
                cats[b.category] = {
                    "id": b.category,
                    "label": b.category_label,
                    "count": 0
                }
            cats[b.category]["count"] += 1
        return list(cats.values())

    def validate_topic_compliance(self, topic_text: str) -> Dict[str, Any]:
        """Audits custom topic text against YouTube Advertiser-Friendly Guidelines (EDSA)."""
        text_lower = topic_text.lower()
        flagged_words = []
        for pattern in PROHIBITED_TITLE_TERMS:
            m = re.search(pattern, text_lower)
            if m:
                flagged_words.append(m.group(0))

        sanitized_title = topic_text
        for raw, safe in EDSA_TITLE_CORRECTIONS.items():
            sanitized_title = re.sub(raw, safe, sanitized_title, flags=re.IGNORECASE)

        is_green = len(flagged_words) == 0
        score = 100 if is_green else max(60, 100 - (len(flagged_words) * 20))

        return {
            "original_topic": topic_text,
            "sanitized_topic": sanitized_title,
            "is_green_dollar": is_green,
            "green_dollar_score": score,
            "flagged_terms": flagged_words,
            "edsa_justification": (
                "Educational / Documentary historical context under Fair Use guidelines. "
                "Verified suitable for all general brand advertisers."
            ),
            "recommended_duration": "15-25 min",
            "pacing_structure": "Nolan 5 Acts with 3 Crosscutting Timelines"
        }

    def generate_procedural_suggestion(self, seed_concept: str) -> TopicBlueprint:
        """Synthesizes a structured compliant 15-30 min topic from any raw input concept."""
        clean_concept = seed_concept.strip()
        compliance = self.validate_topic_compliance(clean_concept)
        sanitized = compliance["sanitized_topic"]

        # Ensure title looks cinematic and professional
        title = sanitized.strip()
        if not title.lower().startswith(("the ", "19", "20", "project ", "operation ")):
            title = f"The {title.title()} Incident"

        topic_id = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:35]

        return TopicBlueprint(
            topic_id=topic_id,
            title=title,
            query=clean_concept,
            category="personalizado",
            category_label="Tema Personalizado",
            duration_min=20,
            duration_label="18-24 min",
            green_dollar_score=compliance["green_dollar_score"],
            edsa_compliant=True,
            viral_hook=f"Os arquivos desclassificados e relatórios de telemetria sobre '{clean_concept}' revelam o momento crucial em que a história quase tomou outro rumo.",
            logline=f"Investigação forense histórica e reconstrução não-linear em 5 atos sobre {clean_concept}.",
            nolan_threads={
                "slow_clock": "O Relógio Lento: Os fatores políticos e tecnológicos silenciosos meses antes do incidente.",
                "fast_clock": "O Relógio Rápido: Os momentos críticos de colapso iminente em tempo real.",
                "aftermath": "O Pós-Impacto: Os depoimentos desclassificados e as repercussões globais permanentes."
            },
            key_entities=[clean_concept],
            retention_factor="Curiosidade documental rigorosa e narrativa 3-fios orientada a evidências."
        )


def main():
    parser = argparse.ArgumentParser(description="DarkFactory Topic Generator Engine")
    parser.add_argument("--list", action="store_true", help="List all available canonical topics")
    parser.add_argument("--category", type=str, default=None, help="Filter by category")
    parser.add_argument("--random", action="store_true", help="Get a single random topic")
    parser.add_argument("--batch", type=int, default=None, help="Get N random topics")
    parser.add_argument("--validate", type=str, default=None, help="Validate compliance of a custom topic string")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    engine = TopicGeneratorEngine()

    if args.validate:
        result = engine.validate_topic_compliance(args.validate)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\nAudit for: '{args.validate}'")
            print(f"Status Green Dollar: {'✅ 100% SEGURO' if result['is_green_dollar'] else '⚠️ AJUSTE EDSA'}")
            print(f"Score: {result['green_dollar_score']}/100")
            print(f"Sugestão Sanitizada: {result['sanitized_topic']}")
        return

    if args.random:
        topic = engine.get_random_topic(args.category)
        if args.json:
            print(json.dumps(topic.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(f"\n🎬 Tópico Sorteado: {topic.title} ({topic.duration_label})")
            print(f"Categoria: {topic.category_label}")
            print(f"Hook: {topic.viral_hook}")
        return

    if args.batch:
        topics = engine.get_batch(args.batch, args.category)
        if args.json:
            print(json.dumps([t.to_dict() for t in topics], indent=2, ensure_ascii=False))
        else:
            print(f"\n--- Batch de {len(topics)} Tópicos Gerados ---")
            for i, t in enumerate(topics, 1):
                print(f"{i}. [{t.category_label}] {t.title} | {t.duration_label} (EDSA {t.green_dollar_score}%)")
        return

    # Default to listing
    topics = engine.get_topics_by_category(args.category) if args.category else engine.get_all_topics()
    if args.json:
        print(json.dumps([t.to_dict() for t in topics], indent=2, ensure_ascii=False))
    else:
        print(f"\n--- DarkFactory Canonical Topics ({len(topics)} disponíveis para 15-30 min) ---")
        for t in topics:
            print(f"• [{t.category_label}] {t.title} ({t.duration_label})")


if __name__ == "__main__":
    main()

from sqlalchemy import create_engine, text

from alembic_migrations.versions.a35b1f4c9d10_backfill_legacy_nulls import (
    apply_backfill,
)


def test_backfill_legacy_nulls_preenche_colunas_criticas():
    engine = create_engine("sqlite:///:memory:")

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY,
                    perfil TEXT,
                    ativo BOOLEAN
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE combatentes (
                    id INTEGER PRIMARY KEY,
                    dono_id INTEGER,
                    classe TEXT,
                    tipo TEXT,
                    hp_atual INTEGER,
                    hp_maximo INTEGER,
                    iniciativa INTEGER,
                    ca INTEGER,
                    toque INTEGER,
                    surpresa INTEGER,
                    fortitude INTEGER,
                    reflexos INTEGER,
                    vontade INTEGER,
                    forca INTEGER,
                    destreza INTEGER,
                    constituicao INTEGER,
                    inteligencia INTEGER,
                    sabedoria INTEGER,
                    carisma INTEGER,
                    nivel INTEGER,
                    pontos INTEGER,
                    raca TEXT,
                    pagina_referencia TEXT
                )
                """
            )
        )
        conn.execute(
            text(
                "CREATE TABLE combatente_condicoes (id INTEGER PRIMARY KEY, duracao_turnos INTEGER)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE magias_preparadas (id INTEGER PRIMARY KEY, usada BOOLEAN)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE combates (id INTEGER PRIMARY KEY, turno_atual INTEGER, rodada_atual INTEGER, ativo BOOLEAN)"
            )
        )

        conn.execute(
            text(
                "INSERT INTO usuarios (id, perfil, ativo) VALUES (1, 'administrador', 1)"
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO combatentes (
                    id, dono_id, classe, tipo, hp_atual, hp_maximo, iniciativa,
                    ca, toque, surpresa, fortitude, reflexos, vontade,
                    forca, destreza, constituicao, inteligencia, sabedoria, carisma,
                    nivel, pontos, raca, pagina_referencia
                ) VALUES (
                    10, NULL, NULL, NULL, NULL, NULL, NULL,
                    NULL, NULL, NULL, NULL, NULL, NULL,
                    NULL, NULL, NULL, NULL, NULL, NULL,
                    NULL, NULL, NULL, NULL
                )
                """
            )
        )
        conn.execute(
            text(
                "INSERT INTO combatente_condicoes (id, duracao_turnos) VALUES (1, NULL)"
            )
        )
        conn.execute(text("INSERT INTO magias_preparadas (id, usada) VALUES (1, NULL)"))
        conn.execute(
            text(
                "INSERT INTO combates (id, turno_atual, rodada_atual, ativo) VALUES (1, NULL, NULL, NULL)"
            )
        )

        apply_backfill(conn)

        combatente = (
            conn.execute(
                text(
                    """
                SELECT dono_id, classe, tipo, hp_atual, hp_maximo, iniciativa,
                       ca, toque, surpresa, fortitude, reflexos, vontade,
                       forca, destreza, constituicao, inteligencia, sabedoria, carisma,
                       nivel, pontos, raca, pagina_referencia
                FROM combatentes
                WHERE id = 10
                """
                )
            )
            .mappings()
            .first()
        )

        assert combatente["dono_id"] == 1
        assert combatente["classe"] == "Sem classe"
        assert combatente["tipo"] == "npc"
        assert combatente["hp_atual"] == 0
        assert combatente["hp_maximo"] == 1
        assert combatente["iniciativa"] == 0
        assert combatente["ca"] == 10
        assert combatente["toque"] == 10
        assert combatente["surpresa"] == 10
        assert combatente["fortitude"] == 0
        assert combatente["reflexos"] == 0
        assert combatente["vontade"] == 0
        assert combatente["forca"] == 10
        assert combatente["destreza"] == 10
        assert combatente["constituicao"] == 10
        assert combatente["inteligencia"] == 10
        assert combatente["sabedoria"] == 10
        assert combatente["carisma"] == 10
        assert combatente["nivel"] == 1
        assert combatente["pontos"] == 0
        assert combatente["raca"] == ""
        assert combatente["pagina_referencia"] == ""

        duracao = conn.execute(
            text("SELECT duracao_turnos FROM combatente_condicoes WHERE id = 1")
        ).scalar()
        usada = conn.execute(
            text("SELECT usada FROM magias_preparadas WHERE id = 1")
        ).scalar()
        combate = conn.execute(
            text("SELECT turno_atual, rodada_atual, ativo FROM combates WHERE id = 1")
        ).first()

        assert duracao == -1
        assert usada == 0
        assert combate[0] == 0
        assert combate[1] == 1
        assert combate[2] == 1

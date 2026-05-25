from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# TOKEN ADMIN
# =========================

ADMIN_TOKEN = "123456"

# =========================
# MODEL
# =========================

class Reserva(BaseModel):
    nome: str
    telefone: str
    data: str
    hora: str

# =========================
# CONEXÃO
# =========================

def conectar():

    conn = sqlite3.connect("reservas.db")

    return conn

# =========================
# CRIAR TABELA
# =========================

conn = conectar()

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS reservas (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT,
    data TEXT,
    hora TEXT,
    status TEXT DEFAULT 'pendente'

)

""")

conn.commit()
conn.close()

# =========================
# CRIAR RESERVA
# =========================

@app.post("/reservar")
def reservar(reserva: Reserva):

    conn = conectar()
    cursor = conn.cursor()

    # verificar horário ocupado

    cursor.execute(
        "SELECT * FROM reservas WHERE data = ? AND hora = ?",
        (reserva.data, reserva.hora)
    )

    horario = cursor.fetchone()

    if horario:

        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Horário já reservado"
        )

    # inserir reserva

    cursor.execute(
        """

        INSERT INTO reservas
        (nome, telefone, data, hora)

        VALUES (?, ?, ?, ?)

        """,
        (
            reserva.nome,
            reserva.telefone,
            reserva.data,
            reserva.hora
        )
    )

    conn.commit()
    conn.close()

    return {
        "msg": "Reserva criada com sucesso"
    }

# =========================
# LISTAR RESERVAS CALENDÁRIO
# =========================

@app.get("/reservas")
def reservas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT data, hora FROM reservas"
    )

    dados = cursor.fetchall()

    conn.close()

    return [

        {
            "data": d[0],
            "hora": d[1]
        }

        for d in dados

    ]

# =========================
# ADMIN - LISTAR TUDO
# =========================

@app.get("/admin/reservas")
def listar(token: str):

    if token != ADMIN_TOKEN:

        raise HTTPException(
            status_code=401,
            detail="Não autorizado"
        )

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """

        SELECT
        id,
        nome,
        telefone,
        data,
        hora,
        status

        FROM reservas

        ORDER BY data ASC

        """
    )

    dados = cursor.fetchall()

    conn.close()

    reservas = []

    for r in dados:

        reservas.append({

            "id": r[0],
            "nome": r[1],
            "telefone": r[2],
            "data": r[3],
            "hora": r[4],
            "status": r[5]

        })

    return reservas

# =========================
# DELETAR RESERVA
# =========================

@app.delete("/admin/reserva/{id}")
def deletar(id: int, token: str):

    if token != ADMIN_TOKEN:

        raise HTTPException(
            status_code=401,
            detail="Não autorizado"
        )

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM reservas WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return {
        "msg": "Reserva deletada"
    }

# =========================
# ALTERAR STATUS
# =========================

@app.put("/admin/status/{id}")
def alterar_status(
    id: int,
    status: str,
    token: str
):

    if token != ADMIN_TOKEN:

        raise HTTPException(
            status_code=401,
            detail="Não autorizado"
        )

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """

        UPDATE reservas

        SET status = ?

        WHERE id = ?

        """,
        (status, id)
    )

    conn.commit()
    conn.close()

    return {
        "msg": "Status atualizado"
    }
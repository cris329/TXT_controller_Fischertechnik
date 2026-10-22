# Futballroboter TXT 4.0 — control PC + Xbox

Control del carro **Futballroboter** (TXT 4.0) desde el PC: teclado, botones web, **mando Xbox** y cámara.

## Requisitos

- TXT 4.0 conectado por USB (IP `192.168.7.2`) o Wi‑Fi
- Python 3.10+ en el PC
- Mando Xbox (opcional) conectado por USB/Bluetooth

## Instalación PC

```bash
pip install -r requirements.txt
```

## 1) Vincular una sola vez (TXT por USB, SSH activo)

```bash
python scripts/install_permanent.py
```

Instala el workspace `Futball`, activa **Autostart** en el TXT y arranca motores + cámara.
Tras reiniciar el controlador ya no hace falta volver a configurar.
Alternativa: `python scripts/deploy_and_run.py` / botón REINICIAR TXT del panel.

## 2) Abrir panel en el PC

```bash
python pc/app.py
```

Abre [http://127.0.0.1:5055](http://127.0.0.1:5055)

Si el TXT está conectado por Wi‑Fi, indica su IP antes de arrancar:

```bash
# Windows PowerShell
$env:TXT_HOST="192.168.1.50"; python pc/app.py
```

### Controles

| Acción | Teclado | Xbox |
|--------|---------|------|
| Avanzar / retroceder | W / S o ↑ / ↓ | Stick izquierdo |
| Girar izquierda / derecha | A / D, Q / E o ← / → | Stick derecho X |
| Empujar pelota | Espacio | A o RB |
| Sonido | Botón SONIDO | — |
| Stop | X | B o Back |

La barra inferior del panel incluye **REINICIAR TXT**, el **D-pad** (avanzar, retroceder y girar), **EMPUJAR** y **SONIDO**.

## Cableado esperado (Futballroboter)

- M1–M4: motores Mecanum + contadores C1–C4
- S1: servo kicker (disparo ~400, reposo ~250)
- Cámara USB en USB1

## Pruebas

```bash
pytest -q
```

"""Gera ícone de raio (.ico multi-resolução) para o app SPDA.

Salva em assets/icone_raio.ico com os tamanhos 16, 32, 48, 64, 128, 256.
Esse ícone pode ser usado no atalho da área de trabalho (.url) e como
referência para favicon/PWA.

Uso:
    python scripts/gerar_icone.py
"""
from pathlib import Path

from PIL import Image, ImageDraw


CORES = {
    "azul_vertec": (31, 78, 121, 255),
    "amarelo_raio": (255, 215, 0, 255),
    "borda_raio": (255, 165, 0, 255),
}


def criar_icone(size: int = 256) -> Image.Image:
    """Desenha um raio amarelo sobre círculo azul, em alta resolução."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo circular azul corporativo
    margin = max(2, size // 32)
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=CORES["azul_vertec"],
    )

    # Raio amarelo — polígono em forma de zig-zag clássico
    # coordenadas calibradas em base 256, escalonadas para o tamanho real
    s = size / 256.0
    bolt = [
        (160 * s, 25 * s),    # topo direito
        (70 * s, 138 * s),    # vértice esquerdo médio
        (118 * s, 138 * s),   # entalhe interno
        (90 * s, 232 * s),    # ponta inferior
        (192 * s, 118 * s),   # vértice direito médio
        (144 * s, 118 * s),   # entalhe interno
        (180 * s, 25 * s),    # topo esquerdo
    ]
    # Borda alaranjada (efeito 3D leve)
    bolt_borda = [(x, y) for (x, y) in bolt]
    draw.polygon(bolt_borda, fill=CORES["borda_raio"])

    # Raio principal (ligeiramente menor para dar contorno)
    bolt_inner = []
    cx, cy = size / 2, size / 2
    for x, y in bolt:
        # encolhe 4% em direção ao centro
        bolt_inner.append((x + (cx - x) * 0.04, y + (cy - y) * 0.04))
    draw.polygon(bolt_inner, fill=CORES["amarelo_raio"])

    return img


def main() -> None:
    base = Path(__file__).parent.parent
    pasta = base / "assets"
    pasta.mkdir(exist_ok=True)

    # Gera imagem 256x256 e salva como ICO multi-tamanho
    img = criar_icone(256)
    ico_path = pasta / "icone_raio.ico"
    img.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    # Salva também PNG para uso em web/manifest se quiser depois
    png_path = pasta / "icone_raio.png"
    img.save(png_path, format="PNG")

    print(f"[OK] Gerado: {ico_path} ({ico_path.stat().st_size:,} bytes)")
    print(f"[OK] Gerado: {png_path} ({png_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

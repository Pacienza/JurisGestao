import os

# Ative com:  set JURIS_DEV=1  (Windows)  |  export JURIS_DEV=1  (Linux/Mac)


'''
COMENTAR O BLOCO ABAIXO ATIVA O MODO DEBUG/DEV
'''
# DEV_MODE = os.getenv("JURIS_DEV", "0") not in {"0", "", "false", "False"}



'''
COMENTAR DAQUI PRA BAIXO ATIVA O MODO PRODUÇÃO/DEPLOY
'''
DEV_MODE = os.getenv("JURIS_DEV", "1")
JURIS_DEV="1"
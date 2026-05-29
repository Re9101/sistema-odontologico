import os
import uvicorn
from app import app

if __name__ == '__main__':
    # Pega a porta do ambiente (Render define isso automaticamente)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Precisa ser 0.0.0.0, não 127.0.0.1
    
    print("=" * 50)
    print("SISTEMA ODONTOLÓGICO INICIADO")
    print("=" * 50)
    print(f"Acesse: http://localhost:{port}/")
    print("Usuário: admin")
    print("Senha: admin123")
    print("=" * 50)
    
    uvicorn.run(app, host=host, port=port)
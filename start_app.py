import sys
from app import app

if __name__ == "__main__":
    port = 5000
    try:
        port = sys.argv[1]
    except:
        pass
    print("Starting webforms service on port", port)
    app.run(host='0.0.0.0', port=port, debug=True)

# That's all!

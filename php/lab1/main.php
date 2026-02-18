<?php
declare(strict_types=1);

$name = $_POST['name'] ?? '';
$name = trim($name);

// простая защита от XSS при выводе
$safeName = htmlspecialchars($name, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

?>
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Результат</title>
</head>
<body>
  <h1>Результат</h1>

  <?php if ($safeName === ''): ?>
    <p>Ты ничего не ввёл</p>
  <?php else: ?>
    <p>Привет, <b><?= $safeName ?></b>! PHP работает</p>
  <?php endif; ?>

  <p><a href="index.html">Назад</a></p>
</body>
</html>
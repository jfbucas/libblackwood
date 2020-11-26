<?php

$SRCEMAIL="test@youpi.com";

$headers = 'From: '.$SRCEMAIL. "\r\n" .
	'Reply-To: '.$SRCEMAIL. "\r\n" .
	'X-Mailer: PHP/' . phpversion();

$to      = $SRCEMAIL;
$subject = 'Solution E2';
$message = 'e2.bucas.name/e2.html'.base64_decode($_GET["solution"]);
mail($to, $subject, $message, $headers);

?> 

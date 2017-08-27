### Emails de Relance Personnalisés

Maia dispose d'une fonctionnalité permettant de créer vos propres modèles d'emails et de choisir celui qui convient le mieux pour chaque patiente.


#### Comment ça marche ?

Allez dans le module "Configuration > Email > Réponse Standard" et créez une nouvelle réponse avec un sujet et un corps de texte.

(Attention, il faut ajouter le module "Configuration" aux icônes du bureau et bien penser à "Recharger" pour qu'il soit accessible)

![Email Personnalisé](/docs/assets/img/appointments/standard_reply1.png)


Maia vous permet aussi de créer vos propres modèles dynamiques.


Par exemple, ce modèle :

![Email Personnalisé](/docs/assets/img/appointments/standard_reply.png)

Générera ce mail pour la patiente :

![Email Personnalisé](/docs/assets/img/appointments/standard_reply2.png)


Il suffit juste de remplacer les mots qui peuvent changer en fonction de la patiente et du rendez-vous et les encadrer avec {{ "{{ }}" }}.

Vous pouvez utiliser les variables suivantes:

- Nom du dossier patient :  patient_record
- Nom complet de la patiente : patient_name
- Prénom de la patiente : patient\_first\_name
- Nom de la patiente : patient\_last\_name
- Nom de la Sage-Femme : practitioner
- Type de Rendez-Vous : appointment_type
- Date du rendez-vous: date
- Heure de début du rendez-vous : start_time
- Durée du rendez-vous : duration


Il ne vous reste plus qu'à sélectionner "Envoyer un Rappel la Veille" dans votre fiche de rendez-vous et de choisir la réponse standard que vous voulez utiliser pour votre patiente.

Si vous laissez la case "Réponse Standard" vide, le mail envoyé utilisera le modèle présenté ci-dessus par défaut.

{next}

# Vacances scolaires françaises

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=infernalK&repository=ha-french-holidays&category=integration)

<details>
    <summary>Cliquez ici pour afficher les instructions détaillées</summary>
    <ol>
        <li>Installation</li>
        <ul>
            <li>
                <u>Via HACS (dépôt personnalisé)</u><br />
                Puisque l'intégration n'est pas disponible directement dans HACS, vous devez ajouter le dépôt personnalisé :
                <ol>
                    <li>Ouvrir HACS et aller dans les Intégrations.</li>
                    <li>Cliquer sur le bouton '...' en haut à droite.</li>
                    <li>Sélectionner "Dépôts personnalisés".</li>
                    <li>Ajouter l'URL du dépôt : https://github.com/infernalK/ha-french-holidays</li>
                    <li>Sélectionner la catégorie "Integration".</li>
                    <li>Chercher "Vacances Scolaires France" et cliquer sur "Installer ce dépôt dans HACS".</li>
                </ol>
            </li>
            <li>
                <u>Manuellement</u><br />
                Télécharger la <a href="https://github.com/infernalK/ha-french-holidays/releases">dernière release</a> au format ZIP et l'extraire dans le répertoire <code>custom_components</code> de votre installation HA.
            </li>
        </ul>
        <li>Redémarrer HA pour qu'il charge l'intégration.</li>
        <li>Aller dans 'Paramètres > Appareils et services' et cliquer sur le bouton bleu '+ Ajouter une intégration'. Chercher 'Vacances Scolaires France' et le sélectionner pour ajouter une zone.</li>
    </ol>
</details>

## Configuration

Pour configurer l'intégration :

1. Aller dans **Paramètres > Appareils et services**.
2. Cliquer sur le bouton **+ Ajouter une intégration**.
3. Rechercher "Vacances scolaires françaises" et la sélectionner.
4. Choisir la zone scolaire souhaitée dans la liste déroulante.
5. Cliquer sur **Soumettre** pour ajouter l'intégration.

Une fois configurée, l'intégration créera automatiquement les entités suivantes pour la zone sélectionnée.

## Fonctionnalités
- un `calendar` avec toutes les vacances à venir pour la zone. Il sert aussi pour vérifier si on est en vacances, parce que le calendrier a un state `ON` si un évènement est en cours et un state `OFF` sinon.
- un `binary_sensor` qui dit si la zone est en vacances aujourd'hui
- un `binary_sensor` qui dit si la zone sera en vacances demain
- un `sensor` "Vacances en cours" avec le nom de la période de vacances, et des attributs supplémentaire. Sa valeur est "Unknown" si pas de vacances en cours
- un `sensor` "Vacances à venir" comme le précédent mais pour les prochaines vacances, n'incluant pas les vacances en cours si c'est le cas (en gros, si vous êtes en pleines vacances de Noel, ca indiquera Vacances d'hiver)
- un `sensor` "Jours avant prochaines vacances" qui indique le nombre de jours avant le début des prochaines vacances
- un `sensor` "Dates prochaines vacances" qui affiche les prochaines vacances au format "Jour Date Mois - Jour Date Mois" (exemple: "Samedi 18 avril - Dimanche 3 mai")

L'intégration se met à jour tous les 120 jours: vu que l'éducation nationale fournit les plannings jusqu'à 2027.

## Mise à jour

<details>
    <summary>Cliquez pour afficher les instructions de mise à jour</summary>
    <ol>
        <li>Mettre à jour les fichiers</li>
        <ul>
            <li>
                <u>Avec HACS</u><br>
                Dans le panneau HACS, une noitification devrait apparaître quand une nouvelle version est disponible. Suivre les instruction de HACS pour mettre à jour.
            </li>
            <li>
                <u>Manuellement</u><br>
                Télécharger la <a href="https://github.com/infernalK/ha-french-holidays/releases">dernière release</a> au format ZIP l'extraire dans le répertoire <code>custom_components</code> de votre installation HA pour écraser l'ancienne version.
            </li>
        </ul>
        <li>Redémarrer HA pour charger les modifications</li>
    </ol>
</details>

## Désinstaller

<details>
    <summary>Cliquez pour afficher les instruction de désinstallation</summary>
    <ol>
        <li>
            <u>Supprimer Vacances Scolaires France de HA:</u><br>
            Aller dans 'Paramètres > Appareils et services'. Dans la section Vacances Scolaires France, cliquer sur le bouton '...', et selectionner 'Supprimer'.
        </li>
        <li>Supprimer les fichiers</li>
        <ul>
            <li>
                <u>Avec HACS</u><br />
                Dans le panneau HACS panel aller sur les intégrations et chercher 'Vacances Scolaires France'.
                Cliquer sur le bouton '...' et sélectionner 'Uninstall'.
            </li>
            <li>
                <u>Manuellement</u><br />
                Dans le répertoire <code>custom_components</code>, supprimer le répertoire <code>french_holiday</code>.
            </li>
        </ul>
        <li>Redémarrer HA pour supprimer toutes les traces de l'intégration.</li>
    </ol>
</details>

## Bugs

Avant de créer un nouveau ticket de bug:

1. Verifiez le nombre de devices sur la page [System Health page](https://my.home-assistant.io/redirect/system_health)
2. Vérifiez les warning et errors sur la page [Logs page](https://my.home-assistant.io/redirect/logs/)
3. Vérifier les **debug logs** sur la page [Debug page](#debug-page) (doit être activé dans les réglages de l'intégration)
4. Vérifier les [tickets **ouverts et fermés**](https://github.com/infernalK/ha-french-holidays/issues?q=is%3Aissue)
5. Partager les [diagnostics de l'integration](https://www.home-assistant.io/integrations/diagnostics/) (à partir de la v2022.2):

- Tous les appareils: Paramètres > Appareils et services > [Intégrations](https://my.home-assistant.io/redirect/integrations/) > **Vacances Scolaires France** > [[...]] > Télécharger les diagnostics
- Un appareil: Paramètres > Appareils et services > [Appareils](https://my.home-assistant.io/redirect/devices/) > (votre appareil) > Télécharger les diagnostics

*Aucune donnée privée n'est transmise, mais vous pouvez supprimer tout ce que vous considererez comme sensible.*
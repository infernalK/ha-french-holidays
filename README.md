# Vacances scolaires françaises

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=infernalK&repository=ha-french-holidays&category=integration)
[![GitHub release](https://img.shields.io/github/v/release/infernalK/ha-french-holidays)](https://github.com/infernalK/ha-french-holidays/releases)
[![License](https://img.shields.io/github/license/infernalK/ha-french-holidays)](LICENSE)

Intégration Home Assistant qui expose les dates des vacances scolaires françaises (zones A, B, C, Corse, DOM-TOM...) sous forme de `calendar`, `binary_sensor` et `sensor`. Les données proviennent de l'[API du Ministère de l'Éducation Nationale](https://data.education.gouv.fr/).

## Sommaire

- [Installation](#installation)
- [Configuration](#configuration)
- [Entités créées](#entités-créées)
- [Mise à jour](#mise-à-jour)
- [Désinstaller](#désinstaller)
- [Bugs](#bugs)

## Installation

L'intégration est référencée officiellement dans HACS (Home Assistant Community Store).

<details>
    <summary>Cliquez ici pour afficher les instructions détaillées</summary>
    <ol>
        <li>Installation</li>
        <ul>
            <li>
                <u>Via HACS</u><br />
                <ol>
                    <li>Ouvrir HACS et aller dans les Intégrations.</li>
                    <li>Chercher "Vacances scolaires françaises".</li>
                    <li>Cliquer sur le résultat puis sur "Télécharger" (ou utiliser le badge ci-dessus).</li>
                </ol>
            </li>
            <li>
                <u>Manuellement</u><br />
                Télécharger la <a href="https://github.com/infernalK/ha-french-holidays/releases">dernière release</a> au format ZIP et l'extraire dans le répertoire <code>custom_components</code> de votre installation HA.
            </li>
        </ul>
        <li>Redémarrer HA pour qu'il charge l'intégration.</li>
        <li>Aller dans 'Paramètres > Appareils et services' et cliquer sur le bouton bleu '+ Ajouter une intégration'. Chercher 'Vacances scolaires françaises' et le sélectionner pour ajouter une zone.</li>
    </ol>
</details>

## Configuration

Pour configurer l'intégration :

1. Aller dans **Paramètres > Appareils et services**.
2. Cliquer sur le bouton **+ Ajouter une intégration**.
3. Rechercher "Vacances scolaires françaises" et la sélectionner.
4. Choisir la zone scolaire souhaitée dans la liste déroulante.
5. Cliquer sur **Soumettre** pour ajouter l'intégration.

Une fois configurée, l'intégration créera automatiquement les entités suivantes pour la zone sélectionnée. Vous pouvez répéter l'opération pour suivre plusieurs zones : chaque zone crée son propre appareil et son propre jeu d'entités.

## Entités créées

### Calendrier

| Entité | Description |
| --- | --- |
| `calendar` | Toutes les vacances à venir pour la zone. Son état est `on` si une période de vacances est en cours, `off` sinon. |

### Capteurs binaires (`binary_sensor`)

| Entité | Description |
| --- | --- |
| Vacances aujourd'hui ? | `on` si la zone est en vacances aujourd'hui. |
| Vacances demain ? | `on` si la zone sera en vacances demain. |

### Capteurs (`sensor`)

| Entité | Description |
| --- | --- |
| Vacances en cours | Nom de la période de vacances en cours, avec les dates et l'année scolaire en attributs. Vaut `Unknown` si pas de vacances en cours. |
| Vacances - dates en cours | Dates de la période en cours, au format "Jour Date Mois - Jour Date Mois" (ex : "Samedi 18 avril - Dimanche 3 mai"). Vaut `Unknown` si pas de vacances en cours. |
| Vacances - jours restants | Nombre de jours restants avant la fin des vacances en cours. Vaut `Unknown` si pas de vacances en cours. |
| Vacances à venir | Nom des prochaines vacances, sans compter celles en cours (si vous êtes en pleines vacances de Noël, ce capteur indiquera "Vacances d'hiver"). |
| Vacances - dates prochaines | Dates des prochaines vacances, même format que ci-dessus. |
| Vacances - jours avant prochaines | Nombre de jours avant le début des prochaines vacances. |

Chaque capteur de type "vacances" expose en attributs `start_date`, `end_date`, `zone` et `année_scolaire`.

L'intégration se met à jour tous les 120 jours, l'Éducation Nationale fournissant les plannings jusqu'en 2027.

## Mise à jour

<details>
    <summary>Cliquez pour afficher les instructions de mise à jour</summary>
    <ol>
        <li>Mettre à jour les fichiers</li>
        <ul>
            <li>
                <u>Avec HACS</u><br>
                Dans le panneau HACS, une notification devrait apparaître quand une nouvelle version est disponible. Suivre les instructions de HACS pour mettre à jour.
            </li>
            <li>
                <u>Manuellement</u><br>
                Télécharger la <a href="https://github.com/infernalK/ha-french-holidays/releases">dernière release</a> au format ZIP et l'extraire dans le répertoire <code>custom_components</code> de votre installation HA pour écraser l'ancienne version.
            </li>
        </ul>
        <li>Redémarrer HA pour charger les modifications</li>
    </ol>
</details>

## Désinstaller

<details>
    <summary>Cliquez pour afficher les instructions de désinstallation</summary>
    <ol>
        <li>
            <u>Supprimer Vacances scolaires françaises de HA :</u><br>
            Aller dans 'Paramètres > Appareils et services'. Dans la section Vacances scolaires françaises, cliquer sur le bouton '...', et sélectionner 'Supprimer'.
        </li>
        <li>Supprimer les fichiers</li>
        <ul>
            <li>
                <u>Avec HACS</u><br />
                Dans le panneau HACS, aller sur les intégrations et chercher 'Vacances scolaires françaises'.
                Cliquer sur le bouton '...' et sélectionner 'Uninstall'.
            </li>
            <li>
                <u>Manuellement</u><br />
                Dans le répertoire <code>custom_components</code>, supprimer le répertoire <code>french_holidays</code>.
            </li>
        </ul>
        <li>Redémarrer HA pour supprimer toutes les traces de l'intégration.</li>
    </ol>
</details>

## Bugs

Avant de créer un nouveau ticket de bug :

1. Vérifiez le nombre d'appareils sur la page [System Health](https://my.home-assistant.io/redirect/system_health).
2. Vérifiez les warnings et erreurs sur la page [Logs](https://my.home-assistant.io/redirect/logs/).
3. Activez et consultez les **logs de débogage** de l'intégration (Paramètres > Appareils et services > Vacances scolaires françaises > '...' > Activer le mode debug), voir la [documentation Home Assistant](https://www.home-assistant.io/docs/configuration/troubleshooting/#debug-logs-and-diagnostics) pour plus de détails.
4. Vérifiez les [tickets **ouverts et fermés**](https://github.com/infernalK/ha-french-holidays/issues?q=is%3Aissue).
5. Partagez les [diagnostics de l'intégration](https://www.home-assistant.io/integrations/diagnostics/) (à partir de la v2022.2) :

- Tous les appareils : Paramètres > Appareils et services > [Intégrations](https://my.home-assistant.io/redirect/integrations/) > **Vacances scolaires françaises** > '...' > Télécharger les diagnostics
- Un appareil : Paramètres > Appareils et services > [Appareils](https://my.home-assistant.io/redirect/devices/) > (votre appareil) > Télécharger les diagnostics

*Aucune donnée privée n'est transmise, mais vous pouvez supprimer tout ce que vous considérerez comme sensible.*

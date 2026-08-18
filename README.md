# Calendario A.D. MARIANISTAS C.D.

Feed `.ics` autoactualizado del calendario de 2ª Andaluza Juvenil (Cádiz),
extraído del PNFG de la RFAF.

## Puesta en marcha

1. Crea un repo **público** (los privados no permiten servir el fichero por raw
   sin token, y complica la suscripción desde el móvil).

2. Estructura:

   ```
   rfaf_calendario.py
   .github/workflows/calendario.yml
   docs/                     ← lo genera el workflow
   ```

3. En **Settings → Actions → General → Workflow permissions**, marca
   *Read and write permissions*. Sin esto el `git push` del bot falla con 403.

4. Pestaña **Actions → Actualizar calendario → Run workflow** para la primera
   ejecución. No esperes al cron.

## Suscribirte

Una vez exista `docs/marianistas.ics`, la URL es:

```
https://raw.githubusercontent.com/USUARIO/REPO/main/docs/marianistas.ics
```

- **iPhone**: Ajustes → Apps → Calendario → Cuentas → Añadir cuenta → Otra →
  Añadir calendario suscrito. Pega la URL. Permite fijar el intervalo de
  actualización.
- **Android / Google Calendar**: hay que darla de alta desde el navegador en
  escritorio (calendar.google.com → Otros calendarios → Desde URL). Google
  refresca cuando quiere, a veces con más de 24 h de retraso.
- **Outlook**: Añadir calendario → Suscribirse desde Internet.

Es **solo lectura**: los eventos se actualizan solos y no puedes editarlos
desde el móvil. Es lo que quieres — si editas, el siguiente refresco te lo pisa.

### Alternativa: GitHub Pages

Si activas Pages sobre la carpeta `/docs`, tendrás una URL más limpia y con
mejor caché:

```
https://USUARIO.github.io/REPO/marianistas.ics
```

## Avisos importantes

- **Los workflows programados se desactivan tras 60 días sin actividad en el
  repo.** GitHub te avisa por email. Un commit cualquiera reactiva el cron.
  Si te pasa a mitad de temporada, el calendario se congela en silencio.
- **El cron de Actions es UTC y no se ajusta al horario de verano.** La hora
  de ejecución se desplaza una hora en marzo y octubre. Da igual para esto.
- **La hora programada no se respeta con exactitud.** GitHub encola los
  workflows y puede retrasarlos bastante en horas punta. Evita el minuto :00.
- El workflow **aborta si detecta menos de 25 eventos**, para no publicar un
  calendario vacío si la RFAF cambia el HTML. Preferible un fallo visible en
  Actions que ver desaparecer los partidos del móvil sin enterarte.

## Frecuencia

Dos veces por semana es suficiente: los cambios de horario y campo se publican
con días de antelación. Bajar a diario no aporta nada y consume minutos de
Actions sin motivo (aunque en repos públicos sean ilimitados).

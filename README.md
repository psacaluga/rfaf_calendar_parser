# Calendario XEREZ DEPORTIVO F.C. FUNDACION "B"

Archivo `.ics` descargable con los eventos de RFAF (Cádiz), extraído del PNFG de la RFAF para importarlo en un calendario personal.

## Puesta en marcha

1. Crea un repo **público** para poder descargar el fichero `.ics` sin autenticación.

2. Estructura:

   ```
   rfaf_calendario.py
   .github/workflows/calendario.yml
   docs/                     ← lo genera el workflow
   ```

3. En **Settings → Actions → General → Workflow permissions**, marca *Read and write permissions*. Sin esto el `git push` del bot falla con 403.

4. Pestaña **Actions → Actualizar calendario → Run workflow** para la primera ejecución. No esperes al cron.

## Importar eventos

Una vez ejecutado el workflow, descarga el archivo:

```
https://github.com/USUARIO/REPO/raw/refs/heads/main/docs/xerez-deportivo-b.ics
```

- **Google Calendar**: abre `calendar.google.com` → Configuración → Importar y exportar → Importar. Selecciona el archivo `.ics` y el calendario de destino.
- **Apple Calendar**: abre Calendario → Archivo → Importar y selecciona el archivo `.ics`.
- **Outlook**: abre Calendario → Agregar calendario → Cargar desde archivo. Selecciona el archivo `.ics` y el calendario de destino.

La importación copia los eventos al calendario elegido. No crea una suscripción,
por lo que los eventos se pueden editar después de importarlos.

Cuando el workflow genere una nueva versión, tendrás que descargarla e importarla
de nuevo. Para evitar duplicados, elimina antes los eventos importados anteriormente
o impórtalos en un calendario separado.

### Descarga desde GitHub Pages

Si activas Pages sobre la carpeta `/docs`, tendrás una URL más limpia para descargar
el archivo:

```
https://USUARIO.github.io/REPO/xerez-deportivo-b.ics
```

## Avisos importantes

- **Los workflows programados se desactivan tras 60 días sin actividad en el repo.** GitHub te avisa por email. Un commit cualquiera reactiva el cron. Si te pasa a mitad de temporada, el calendario se congela en silencio.
- **El cron de Actions es UTC y no se ajusta al horario de verano.** La hora de ejecución se desplaza una hora en marzo y octubre. Da igual para esto.
- **La hora programada no se respeta con exactitud.** GitHub encola los workflows y puede retrasarlos bastante en horas punta. Evita el minuto :00.
- El workflow **aborta si detecta menos de 25 eventos**, para no publicar un calendario vacío si la RFAF cambia el HTML. Preferible un fallo visible en Actions que ver desaparecer los partidos del móvil sin enterarte.

## Frecuencia

Dos veces por semana es suficiente: los cambios de horario y campo se publican con días de antelación. Bajar a diario no aporta nada y consume minutos de Actions sin motivo (aunque en repos públicos sean ilimitados).

## Personalizar otro equipo

El script es genérico. La ejecución sin argumentos usa la URL y el equipo del Xerez
definidos en `rfaf_calendario.py`. Para otro calendario, indica la URL completa de la
RFAF, el nombre exacto del equipo tal como aparece en la página y un identificador
sin espacios para los ficheros:

```bash
python3 rfaf_calendario.py \
   --url "https://www.rfaf.es/pnfg/NPcd/NFG_VisCalendario_Vis?cod_primaria=...&codtemporada=...&codcompeticion=...&codgrupo=..." \
   --equipo "NOMBRE DEL EQUIPO" \
   --slug nombre-equipo
```

Esto genera dentro de `docs/` una carpeta `nombre-equipo-AAAA-MM-DD` con
`nombre-equipo.ics` y `nombre-equipo.json`. El mismo comando puede usarse con un
HTML descargado localmente, pasando el fichero como primer argumento.


https://www.rfaf.es/pnfg/NPcd/NFG_VisCalendario_Vis?cod_primaria=1000120&codtemporada=22&codcompeticion=49505530&codgrupo=49603134

# Fonts

Self-hosted, no runtime requests to Google. Both families are licensed under the SIL Open Font License 1.1 (https://openfontlicense.org), which allows free use, embedding and redistribution, including on websites.

| File | Family | Weight | Subset | Source |
|---|---|---|---|---|
| anton-400-latin.woff2 | Anton | 400 | latin | https://fonts.gstatic.com/s/anton/v27/1Ptgg87LROyAm3Kz-C8CSKlv.woff2 |
| anton-400-latin-ext.woff2 | Anton | 400 | latin-ext | https://fonts.gstatic.com/s/anton/v27/1Ptgg87LROyAm3K9-C8CSKlvPfE.woff2 |
| inter-variable-latin.woff2 | Inter | variable 100 to 900 | latin | https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7W0Q5nw.woff2 |
| inter-variable-latin-ext.woff2 | Inter | variable 100 to 900 | latin-ext | https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7W0Q5n-wU.woff2 |

Fetched 19 Oct 2026 from the Google Fonts css2 API (family=Anton and family=Inter:wght@100..900) using a modern Chrome user agent, then the woff2 files from fonts.gstatic.com.

Anton is by Vernon Adams (Google Fonts). Inter is by Rasmus Andersson.

## Suggested @font-face

Use unicode-range so the latin-ext files only load if a page needs those characters. Preload only the two latin files.

```css
@font-face { font-family: "Anton"; font-style: normal; font-weight: 400; font-display: swap;
  src: url("../fonts/anton-400-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
@font-face { font-family: "Anton"; font-style: normal; font-weight: 400; font-display: swap;
  src: url("../fonts/anton-400-latin-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF; }
@font-face { font-family: "Inter"; font-style: normal; font-weight: 100 900; font-display: swap;
  src: url("../fonts/inter-variable-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
@font-face { font-family: "Inter"; font-style: normal; font-weight: 100 900; font-display: swap;
  src: url("../fonts/inter-variable-latin-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF; }
```

Preload (crossorigin is required for font preloads even when same origin):

```html
<link rel="preload" href="/fonts/anton-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-variable-latin.woff2" as="font" type="font/woff2" crossorigin>
```

The build copies src/fonts/*.woff2 into public/fonts/, and the preload hrefs must go through the BASE_PATH setting.

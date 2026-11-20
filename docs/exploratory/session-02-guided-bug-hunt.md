# Session 02: Guided bug hunt (full app)

## Charter
**Explore** the whole Toolshop app (catalog, product detail, account, profile, contact form, navigation)
**with** the site's built-in Bug Hunting Guide as a starting map, going beyond it wherever something looked off
**to discover** defects across functionality, data, text, visuals, and validation.

| | |
|---|---|
| **Tester** | PK Ganow |
| **Environment** | https://with-bugs.practicesoftwaretesting.com (Toolshop v5.0 with bugs) |
| **Browser / OS** | Chrome, macOS |
| **Date** | 2026-11-19 |
| **Reference ("what it should do")** | https://practicesoftwaretesting.com (main build) |

## Result
The guide's tracker credited **25 bugs** across all eight hunt areas.
Comparing my notes with the guide afterwards, **9 of my findings are not in the guide** (one was later downgraded after checking the data), and on 2 more I went further than the guide's description.
Guide hunt numbers are listed so it's clear which findings were guided and which were my own.

## Findings

**Source:** *Independent* = not in the guide. *Guide #n* = covered by guide hunt n. *Extends guide #n* = guided, but I found more than the guide describes.

| # | Area | Finding | Source | Severity (draft) | Issue |
|---|------|---------|--------|------------------|-------|
| 1 | Catalog: categories | The 3rd category in the filter list is labelled **"Undefined"**; selecting it shows no products | **Independent** | Major || [#3](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/3) |
| 2 | Catalog: brand filter | Filter lists **10 placeholder brands ("Brand name 1–10")**, 8 of which have no products, so picking them shows nothing. *Checked via the API: brands 3–10 have 0 products, so the filter itself works; the issue is offering empty choices.* | **Independent** | Minor (data/UX) | |
| 3 | Catalog: price range | Moving the **price range slider doesn't change** which products are shown | **Independent** | Major || [#2](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/2) |
| 4 | Product detail | **CO₂ rating info tip** shows its "?" marker, but the tip never appears on hover | **Independent** | Minor | |
| 5 | Text | "Favorites" is spelled **two ways** across the site (Favorites / Favourites) | **Independent** | Cosmetic | |
| 6 | Text: user menu | Menu items use inconsistent capitalization ("My account", "My favorites"…) *(style choice: confirm the intended standard)* | **Independent** | Cosmetic | |
| 7 | Profile | Clicking **Update Profile** fails with **"resource not found"** | **Independent** | Major || [#4](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/4) |
| 8 | Contact form | Message field placeholder reads **"Massage"** | **Independent** | Cosmetic | |
| 9 | Contact form | The upload help text says **txt, pdf, or jpg** are allowed, but only .txt is accepted; .jpg is rejected with "we only accept txt files" | **Extends guide #23** (guide: pdf/jpg rejected; I also found the help text contradicts the rule) | Major || [#7](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/7) |
| 10 | Catalog: sort | Sorting is **reversed for every option**: name, price, and CO₂. CO₂ sort also lists products **without** an ECO badge | **Extends guide #6** (guide: price only) | Major || [#6](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/6) |
| 11 | Product detail | **+ / −** quantity buttons do nothing (no error shown); typing a quantity and pressing + also does nothing | Guide #7 | Major | [#8](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/8) |
| 12 | Product detail | **Add to favourites** shows a red error toast and adds nothing | Guide #7 | Major | [#10](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/10) |
| 13 | Product detail | **Add to cart** and **Add to favourites** buttons overlap | Guide #10 | Minor | |
| 14 | Navigation | **Home** link goes to the Contact page (even from the home page); the only way home is the broken logo | Guide #15 | Major | [#11](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/11) |
| 15 | Navigation | User menu shows **"User Data not found"** instead of the user's name (also caught by the automated login test on 2026-11-18, but not reproduced by hand that day: intermittent) | Guide #11 | Minor | [#12](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/12) |
| 16 | Profile | **"City not found"** shown in the City field | Guide #12 | Minor | |
| 17 | Profile | **Password update** shows success and logs the user out, but the new password then fails to log in (user locked out) | Guide #21 | Critical || [#5](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/5) |
| 18 | Visual | Site **logo** and **search icon** images are broken | Guide #8 | Minor | |
| 19 | Visual | **Slip Joint Pliers** image missing in the product grid, but present on its detail page | Guide #8 | Minor | |
| 20 | Text | Typos: **"Sorth"**, **"Serch"**, **"Reltded products"** | Guide #9 | Cosmetic | |
| 21 | Text | **"Contakt"** in the top navigation | Guide #15 | Cosmetic | |
| 22 | Login | No field validation: invalid email + blank password gives no message | Guide #20 | Major | [#1](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/1) |
| 23 | Product detail / cart | **Cart badge stays at 1** after a second **Add to cart** of the same product (expected 2) | **Independent** | Major | [#9](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/9) |

**Note on finding 23:** seen by hand on 2026-11-19, recorded on 2026-11-20 from the H-004 re-run (`tests/ui/test_product_and_cart.py::test_cart_count_follows_each_add` fails on with-bugs, passes on main). It may be linked to finding 11 (if Add to cart reads the broken quantity); not yet confirmed.

## Not yet covered
- Guide hunts I didn't record in my notes: cart total, payment gateway, checkout form, cart delete button (#2–#5), chainsaw category (#5), invoices (#13), contact subject dropdown (#14), and the advanced security, registration, and accessibility hunts (#16–#19, #22, #24–#26). These are candidates for follow-up sessions.

## Follow-up charters
- Unguided session on **checkout and invoices**, using the main build as the reference.
- **Security basics** session (account lockout, error messages that leak information, authorization on the API), on this practice environment only.
- **Accessibility** session with Lighthouse and keyboard-only navigation.

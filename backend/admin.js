const ADMIN_DEFAULTS = {
  apiBase: "/api/v1",
  brandName: "Беатрис",
  panelName: "Административная панель",
  documentTitle: "Административная панель",
  homeUrl: "/admin",
  locale: "ru-RU",
  currencySymbol: "₸",
  overviewStartDate: "2026-05-14",
  phonePlaceholder: "+77000000000",
  paginationSizes: [10, 20, 50, 100],
  // Контакты клиники (выводятся в боковой панели)
  clinicPhone: "+7 700 000 00 00",
  clinicEmail: "",
  clinicAddress: "",
  clinicHours: "Пн–Сб 09:00–20:00",
  // Юридические реквизиты
  legalName: "",
  bin: "",
  licenseNumber: "",
  licenseFileUrl: "",
  // Параметры записи пациентов
  defaultSlotMinutes: 30,
  bookingHorizonDays: 30,
  minLeadHours: 2,
  onlineBookingEnabled: true,
  // Уведомления
  remindersEnabled: true,
  reminderLeadHours: 24,
  ...(window.ADMIN_CONFIG || {}),
};

const ADMIN_CONFIG = { ...ADMIN_DEFAULTS };

const API_BASE = ADMIN_CONFIG.apiBase.replace(/\/+$/, "");

const appointmentStatuses = {
  pending: "Новая заявка",
  confirmed: "Подтверждена",
  completed: "Завершена",
  cancelled: "Отменена",
};

const appointmentContactStatuses = {
  not_contacted: "Не связывались",
  contacted: "Связались",
  agreed: "Новое время согласовано",
  declined: "Пациент отказался",
};

const orderStatuses = {
  created: "Создан",
  paid: "Оплачен",
  processing: "В отправке",
  delivered: "Доставлен",
  cancelled: "Отменен",
};

const paymentStatuses = {
  pending: "Ожидает",
  paid: "Оплачено",
  failed: "Ошибка",
  refunded: "Возврат",
};

const paymentMethods = {
  card_online: "Картой онлайн",
  cash_on_delivery: "Наличными при получении",
};

const deliveryMethods = {
  courier: "Курьер",
  pickup: "Самовывоз",
};

let accessToken = null;
let state = {
  appointments: [],
  services: [],
  specialists: [],
  products: [],
  serviceCategories: [],
  productCategories: [],
  orders: [],
  users: [],
  schedule: [],
  reviews: [],
  appointmentsSort: { key: "date", dir: "desc" },
  productsSort: { key: "title", dir: "asc" },
  ordersSort: { key: "createdAt", dir: "desc" },
  servicesSort: { key: "title", dir: "asc" },
  specialistsSort: { key: "fullName", dir: "asc" },
  usersSort: { key: "createdAt", dir: "desc" },
  reviewsSort: { key: "author", dir: "asc" },
};

const DEFAULT_PER_PAGE = ADMIN_CONFIG.paginationSizes[0] || 10;
const tablePages = {
  appointments: { page: 1, perPage: DEFAULT_PER_PAGE, search: "" },
  services: { page: 1, perPage: DEFAULT_PER_PAGE, search: "" },
  specialists: { page: 1, perPage: DEFAULT_PER_PAGE, search: "" },
  users: { page: 1, perPage: DEFAULT_PER_PAGE, search: "" },
  products: { page: 1, perPage: DEFAULT_PER_PAGE, search: "" },
  orders: { page: 1, perPage: DEFAULT_PER_PAGE, search: "" },
  reviews: { page: 1, perPage: DEFAULT_PER_PAGE, search: "" },
};

const PANEL_TO_SCOPE = {
  appointments: "appointments",
  services: "services",
  specialists: "specialists",
  store: "products",
  orders: "orders",
  users: "users",
  reviews: "reviews",
};

let activeReviewFilter = "all";
let activeUserRole = "all";
const appointmentFilters = {
  patient: "",
  serviceId: "",
  specialistId: "",
  date: "",
};

function renderScope(scope) {
  switch (scope) {
    case "appointments": return renderAppointments();
    case "services": return renderServices();
    case "specialists": return renderSpecialists();
    case "users": return renderUsers();
    case "products": return renderProducts();
    case "orders": return renderOrders();
    case "reviews": return renderReviews();
  }
}
let activeStatusFilter = "requests";
let selectedAppointmentId = null;
let selectedServiceCategoryId = null;
let currentPanel = "overview";

const formatMoney = (value) => `${Number(value).toLocaleString(ADMIN_CONFIG.locale)} ${ADMIN_CONFIG.currencySymbol}`;
const formatDateTime = (value) =>
  value
    ? new Date(value).toLocaleString(ADMIN_CONFIG.locale, {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";
const formatDate = (value) =>
  value
    ? new Date(value).toLocaleDateString(ADMIN_CONFIG.locale, {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      })
    : "—";
const formatDateAndTime = (date, time) =>
  date ? `${formatDate(`${date}T00:00:00`)}, ${time || "00:00"}` : "—";
let OVERVIEW_START_DATE = new Date(`${ADMIN_CONFIG.overviewStartDate}T00:00:00`);

function getOverviewDate() {
  const now = new Date();
  const localToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return localToday < OVERVIEW_START_DATE ? OVERVIEW_START_DATE : localToday;
}

function formatDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatDisplayDate(date) {
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${day}.${month}.${date.getFullYear()}`;
}

// --- Sort / pagination helpers ---

function sortRows(rows, key, dir, accessor) {
  const sign = dir === "desc" ? -1 : 1;
  return [...rows].sort((a, b) => {
    const va = accessor(a, key);
    const vb = accessor(b, key);
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    if (typeof va === "number" && typeof vb === "number") return (va - vb) * sign;
    return String(va).localeCompare(String(vb), "ru") * sign;
  });
}

function pageSlice(rows, page, perPage) {
  return rows.slice((page - 1) * perPage, page * perPage);
}

function renderSortIcons(scope, sort) {
  document.querySelectorAll(`[data-sort-${scope}]`).forEach((th) => {
    const key = th.dataset[`sort${scope.charAt(0).toUpperCase() + scope.slice(1)}`];
    const arrow = th.querySelector(".sort-arrow");
    if (!arrow) return;
    if (key === sort.key) {
      arrow.textContent = sort.dir === "asc" ? "▲" : "▼";
      arrow.classList.add("is-active");
    } else {
      arrow.textContent = "↕";
      arrow.classList.remove("is-active");
    }
  });
}

function renderTableFooter(targetId, total, page, perPage, prefix) {
  const totalPages = Math.max(1, Math.ceil(total / perPage));
  const from = total === 0 ? 0 : (page - 1) * perPage + 1;
  const to = Math.min(page * perPage, total);
  const sizes = ADMIN_CONFIG.paginationSizes;
  document.querySelector(targetId).innerHTML = `
    <div class="pagination-info">Показано ${from}–${to} из ${total}</div>
    <div class="pagination-controls">
      <label class="pagination-size">На странице
        <select data-pagination-size="${prefix}">
          ${sizes.map((n) => `<option value="${n}" ${n === perPage ? "selected" : ""}>${n}</option>`).join("")}
        </select>
      </label>
      <button class="status-action" type="button" data-pagination="${prefix}" data-pagination-dir="prev" ${page <= 1 ? "disabled" : ""}>‹</button>
      <span class="pagination-page">${page} / ${totalPages}</span>
      <button class="status-action" type="button" data-pagination="${prefix}" data-pagination-dir="next" ${page >= totalPages ? "disabled" : ""}>›</button>
    </div>
  `;
}

function paginate(scope, rows, footerId) {
  const st = tablePages[scope];
  const totalPages = Math.max(1, Math.ceil(rows.length / st.perPage));
  st.page = Math.min(Math.max(1, st.page), totalPages);
  renderTableFooter(footerId, rows.length, st.page, st.perPage, scope);
  return pageSlice(rows, st.page, st.perPage);
}

function matchesSearch(scope, text) {
  const needle = tablePages[scope].search;
  return !needle || text.toLowerCase().includes(needle);
}

const CYRILLIC_TO_LATIN = {
  а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ё: "yo", ж: "zh", з: "z",
  и: "i", й: "y", к: "k", л: "l", м: "m", н: "n", о: "o", п: "p", р: "r",
  с: "s", т: "t", у: "u", ф: "f", х: "h", ц: "c", ч: "ch", ш: "sh", щ: "sch",
  ъ: "", ы: "y", ь: "", э: "e", ю: "yu", я: "ya",
};

function slugify(value) {
  return value
    .toLowerCase()
    .split("")
    .map((ch) => (ch in CYRILLIC_TO_LATIN ? CYRILLIC_TO_LATIN[ch] : ch))
    .join("")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function wireAutoSlug(formSelector) {
  const form = document.querySelector(formSelector);
  if (!form) return;
  const titleInput = form.elements.title;
  const slugInput = form.elements.slug;
  if (!titleInput || !slugInput) return;
  slugInput.addEventListener("input", () => {
    slugInput.dataset.userEdited = "true";
  });
  titleInput.addEventListener("input", () => {
    if (slugInput.dataset.userEdited === "true") return;
    slugInput.value = slugify(titleInput.value);
  });
}

async function apiFetch(path, options = {}, allowRefresh = true) {
  const headers = { "Content-Type": "application/json" };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: { ...headers, ...(options.headers || {}) },
  });

  if (
    res.status === 401 &&
    allowRefresh &&
    accessToken &&
    !path.startsWith("/auth/refresh") &&
    !path.endsWith("/auth/login")
  ) {
    if (await refreshAccessToken()) {
      return apiFetch(path, options, false);
    }
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail));
  }
  if (res.status === 204) return null;
  return res.json();
}

async function refreshAccessToken() {
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) return false;
    const data = await res.json();
    accessToken = data.accessToken;
    return true;
  } catch (_) {
    return false;
  }
}

async function tryRestoreSession() {
  if (!(await refreshAccessToken())) return false;
  try {
    const me = await apiFetch("/admin/auth/me");
    if (me.role !== "admin") {
      accessToken = null;
      return false;
    }
    return true;
  } catch (_) {
    accessToken = null;
    return false;
  }
}

async function enterAdmin() {
  await loadAll();
  await loadSettings();
  showAdminShell();
  renderAll();
  bindEvents();
}

async function downloadExport(path, baseName) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      credentials: "include",
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail));
    }
    const blob = await res.blob();
    const today = new Date().toISOString().slice(0, 10);
    const filename = `${baseName}_${today}.csv`;
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (err) {
    showToast(`Ошибка экспорта: ${err.message}`);
  }
}

function attachImagePicker(input) {
  if (!input || input.dataset.imagePickerWired === "true") return;
  const folder = input.dataset.imageFolder;
  if (!folder) return;

  input.type = "hidden";
  input.dataset.imagePickerWired = "true";

  const wrapper = document.createElement("div");
  wrapper.className = "image-picker";

  const status = document.createElement("span");
  status.className = "image-picker__status";

  const uploadBtn = document.createElement("button");
  uploadBtn.type = "button";
  uploadBtn.className = "btn btn-secondary image-picker__upload";
  uploadBtn.textContent = "Загрузить";

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "btn btn-secondary image-picker__remove";
  removeBtn.textContent = "Удалить";

  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/jpeg,image/png,image/webp";
  fileInput.style.display = "none";

  wrapper.append(status, uploadBtn, removeBtn, fileInput);
  input.insertAdjacentElement("afterend", wrapper);

  const refresh = () => {
    const value = input.value || "";
    if (value) {
      const name = value.split("/").pop().split("?")[0];
      status.textContent = name;
      status.classList.add("has-file");
      removeBtn.disabled = false;
    } else {
      status.textContent = "Файл не загружен";
      status.classList.remove("has-file");
      removeBtn.disabled = true;
    }
  };

  refresh();
  input.addEventListener("change", refresh);

  uploadBtn.addEventListener("click", () => fileInput.click());
  removeBtn.addEventListener("click", () => {
    input.value = "";
    refresh();
  });

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files?.[0];
    if (!file) return;
    uploadBtn.disabled = true;
    const previousLabel = uploadBtn.textContent;
    uploadBtn.textContent = "Загружаем…";
    try {
      const fd = new FormData();
      fd.append("file", file);
      const headers = accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
      const res = await fetch(`${API_BASE}/admin/uploads/image?folder=${encodeURIComponent(folder)}`, {
        method: "POST",
        headers,
        body: fd,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail));
      }
      const data = await res.json();
      input.value = data.url || "";
      refresh();
      showToast("Изображение загружено");
    } catch (err) {
      showToast(`Ошибка загрузки: ${err.message}`);
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.textContent = previousLabel;
      fileInput.value = "";
    }
  });
}

function wireAllImagePickers() {
  document.querySelectorAll("input[data-image-folder]").forEach(attachImagePicker);
}

async function login(phone, password, remember = true) {
  const data = await apiFetch("/admin/auth/login", {
    method: "POST",
    body: JSON.stringify({ phone, password, remember }),
  });
  if (data.user.role !== "admin") {
    throw new Error("Доступ разрешён только администраторам");
  }
  accessToken = data.accessToken;
}

async function loadAll() {
  const [appts, svcs, specs, prods, serviceCats, productCats, ords, usrs, sched, revs] = await Promise.all([
    apiFetch("/admin/appointments?limit=100"),
    apiFetch("/admin/services?limit=100"),
    apiFetch("/admin/specialists?limit=100"),
    apiFetch("/admin/products?limit=100"),
    apiFetch("/service-categories"),
    apiFetch("/admin/product-categories"),
    apiFetch("/admin/orders?limit=100"),
    apiFetch("/admin/users?limit=100"),
    apiFetch("/admin/doctor-schedule?limit=100"),
    apiFetch("/admin/reviews?limit=100"),
  ]);
  state.appointments = appts.items;
  state.services = svcs.items;
  state.specialists = specs.items;
  state.products = prods.items;
  state.serviceCategories = serviceCats;
  state.productCategories = productCats;
  state.orders = ords.items;
  state.users = usrs.items;
  state.schedule = sched.items;
  state.reviews = revs.items;
  if (!selectedAppointmentId && state.appointments.length > 0) {
    selectedAppointmentId = state.appointments[0].id;
  }
}

// --- Render ---

function statusBadge(status, labels) {
  return `<span class="status-badge ${status}">${labels[status] || status}</span>`;
}

function renderMetrics() {
  const overviewDate = getOverviewDate();
  const today = formatDateKey(overviewDate);
  const todaysAppointments = state.appointments.filter((a) => a.date === today);
  const pending = state.appointments.filter((a) => a.status === "pending");
  const revenue = state.orders
    .filter((o) => o.paymentStatus === "paid")
    .reduce((sum, o) => sum + (Number(o.totalPrice) || 0), 0);
  const activeServices = state.services.filter((s) => s.isActive !== false);
  const totalStock = state.products.reduce((sum, p) => sum + (Number(p.stock) || 0), 0);

  document.querySelector("#overviewDate").textContent = formatDisplayDate(overviewDate);
  document.querySelector("#metricAppointments").textContent = todaysAppointments.length;
  document.querySelector("#metricPending").textContent = pending.length;
  document.querySelector("#metricRevenue").textContent = formatMoney(revenue);
  document.querySelector("#metricServices").textContent = activeServices.length;
  document.querySelector("#metricStock").textContent = totalStock;
}

function renderPriorityList() {
  const priority = state.appointments.filter((a) => a.status === "pending");
  const container = document.querySelector("#priorityList");

  if (priority.length === 0) {
    container.innerHTML = `<p class="muted">Нет записей, ожидающих подтверждения.</p>`;
    return;
  }

  container.innerHTML = priority
    .map(
      (a) => `
      <article
        class="action-item"
        data-row-search="${a.patientName} ${a.patientPhone || ""} ${a.service.title} ${a.specialist.fullName} ${a.comment || ""}"
        data-select-appointment="${a.id}"
      >
        <header class="action-item-head">
          <div class="action-item-patient">
            <strong>${a.patientName}</strong>
            <small>${a.patientPhone || "телефон не указан"}</small>
          </div>
          <div class="appointment-badge-group">
            ${statusBadge(a.status, appointmentStatuses)}
            ${a.status === "pending" ? scheduleMatchBadge(a) : ""}
          </div>
        </header>
        <dl class="action-item-body">
          <div><dt>Услуга</dt><dd>${a.service.title}</dd></div>
          <div><dt>Специалист</dt><dd>${a.specialist.fullName}</dd></div>
          <div><dt>Когда</dt><dd>${formatDateAndTime(a.date, a.time)}</dd></div>
          ${a.comment ? `<div><dt>Комментарий</dt><dd>${a.comment}</dd></div>` : ""}
        </dl>
        <div class="action-item-actions">
          <button class="status-action" type="button" data-appointment="${a.id}" data-next-status="confirmed">Подтвердить</button>
          <button class="status-action danger" type="button" data-appointment="${a.id}" data-next-status="cancelled">Отменить</button>
        </div>
      </article>
    `
    )
    .join("");
}

function renderSchedule() {
  const scheduleCard = (slot, showActions) => `
      <article class="timeline-item" data-row-search="${slot.specialist.fullName} ${slot.date} ${slot.startTime} ${slot.endTime}">
        <time>${slot.startTime}–${slot.endTime}</time>
        <div>
          <strong>${slot.specialist.fullName}</strong>
          <small>${formatDate(`${slot.date}T00:00:00`)}</small>
          ${slot.isAvailable ? statusBadge("confirmed", { confirmed: "Доступно" }) : statusBadge("cancelled", { cancelled: "Скрыто" })}
          ${
            showActions
              ? `<div class="table-actions">
                  <button class="status-action" type="button" data-schedule-edit="${slot.id}">Изменить</button>
                  ${slot.isAvailable
                    ? `<button class="status-action danger" type="button" data-schedule-delete="${slot.id}">Скрыть</button>`
                    : `<button class="status-action" type="button" data-schedule-restore="${slot.id}">Вернуть</button>`}
                  <button class="status-action danger" type="button" data-schedule-hard-delete="${slot.id}">Удалить</button>
                </div>`
              : ""
          }
        </div>
      </article>
    `;
  const previewHtml = state.schedule.map((slot) => scheduleCard(slot, false)).join("");
  const empty = "<p style='padding:1rem;color:var(--text-2)'>Расписание пусто</p>";
  document.querySelector("#schedulePreview").innerHTML = previewHtml || empty;
  renderScheduleWeek();
}

const WEEK_DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
let scheduleMonthDate = new Date(new Date().getFullYear(), new Date().getMonth(), 1);

function addDays(d, n) {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}

function localDateKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function renderScheduleWeek() {
  const grid = document.querySelector("#scheduleWeekGrid");
  if (!grid) return;

  const monthStart = new Date(scheduleMonthDate.getFullYear(), scheduleMonthDate.getMonth(), 1);
  const offset = (monthStart.getDay() + 6) % 7;
  const calendarStart = addDays(monthStart, -offset);
  const todayKey = localDateKey(new Date());
  const parts = [];

  document.querySelector("#scheduleWeekRange").textContent = monthStart.toLocaleDateString(
    ADMIN_CONFIG.locale,
    { month: "long", year: "numeric" },
  );

  WEEK_DAY_NAMES.forEach((name) => {
    parts.push(`<div class="swg-cell swg-header">${name}</div>`);
  });

  for (let index = 0; index < 42; index += 1) {
    const day = addDays(calendarStart, index);
    const dateKey = localDateKey(day);
    const daySlots = state.schedule
      .filter((slot) => slot.date === dateKey)
      .sort((a, b) => a.startTime.localeCompare(b.startTime));
    const classes = ["swg-month-day"];
    if (day.getMonth() !== monthStart.getMonth()) classes.push("is-outside");
    if (dateKey === todayKey) classes.push("is-today");
    const slotsHtml = daySlots.map((slot) => {
      const statusClass = slot.isAvailable ? "is-available" : "is-hidden";
      return `
        <button type="button" class="swg-slot ${statusClass}" data-schedule-edit="${slot.id}" title="${slot.specialist.fullName}">
          <strong>${slot.startTime}–${slot.endTime}</strong>
          <span>${slot.specialist.fullName}</span>
        </button>`;
    }).join("");
    parts.push(
      `<div class="${classes.join(" ")}">
        <div class="swg-day-number">${day.getDate()}</div>
        <div class="swg-day-slots">${slotsHtml}</div>
      </div>`
    );
  }

  grid.style.gridTemplateRows = "";
  grid.innerHTML = parts.join("");
}

function renderAppointmentDetail(appointmentId = null) {
  const targetId = appointmentId || selectedAppointmentId;
  const appointment =
    state.appointments.find((a) => a.id === targetId) || state.appointments[0];
  if (!appointment) {
    document.querySelector("#appointmentDetail").innerHTML = "<p>Запись не выбрана.</p>";
    return;
  }
  const contactStatus = appointment.patientContactStatus || "not_contacted";
  const eligibleSpecialists = state.specialists.filter((specialist) =>
    specialist.services?.some((service) => service.id === appointment.service.id)
  );
  const specialistOptions = eligibleSpecialists
    .map(
      (specialist) =>
        `<option value="${specialist.id}" ${specialist.id === appointment.specialist.id ? "selected" : ""}>${specialist.fullName}</option>`
    )
    .join("");
  const historyHtml = appointment.statusHistory?.length
    ? appointment.statusHistory
        .map(
          (item) => `
            <li>
              <strong>${appointmentStatuses[item.previousStatus] || item.previousStatus} → ${appointmentStatuses[item.newStatus] || item.newStatus}</strong>
              <span>${formatDateTime(item.createdAt)} · ${item.adminName || "администратор"}</span>
            </li>
          `
        )
        .join("")
    : `<li><span>История статусов пока пуста.</span></li>`;
  document.querySelector("#appointmentDetail").innerHTML = `
    <div>
      <p class="eyebrow">Детали записи${appointment.appointmentNumber ? ` · <span class="appt-number">${appointment.appointmentNumber}</span>` : ""}</p>
      <h3>${appointment.patientName}</h3>
    </div>
    ${statusBadge(appointment.status, appointmentStatuses)}
    ${
      appointment.status === "pending"
        ? isAppointmentInSchedule(appointment)
          ? `<p class="schedule-hint ok">Время совпадает с расписанием специалиста&nbsp;—&nbsp;можно&nbsp;подтвердить.</p>`
          : `<p class="schedule-hint warn">Время вне текущего расписания специалиста - надо связаться.</p>`
        : ""
    }
    <dl>
      <div><dt>Телефон</dt><dd>${appointment.patientPhone}</dd></div>
      <div><dt>Услуга</dt><dd>${appointment.service.title}</dd></div>
      <div><dt>Специалист</dt><dd>${appointment.specialist.fullName}</dd></div>
    </dl>
    <section class="status-history" aria-label="История статусов">
      <h4>История статусов</h4>
      <ul>${historyHtml}</ul>
    </section>
  `;
}

function openAppointmentEditDialog(appointmentId) {
  const appointment = state.appointments.find((a) => a.id === appointmentId);
  if (!appointment) return;
  const dialog = document.querySelector("#appointmentEditDialog");

  const visibleNumber = appointment.appointmentNumber || String(appointment.id || "—").slice(0, 8).toUpperCase();
  document.querySelector("#apptEditKind").textContent = appointment.status === "pending" ? "Заявка" : "Запись";
  document.querySelector("#apptEditNumber").textContent = visibleNumber;
  document.querySelector("#apptEditTitle").textContent = appointment.patientName;
  document.querySelector("#apptEditStatusBadge").innerHTML = `
    ${statusBadge(appointment.status, appointmentStatuses)}
    ${appointment.status === "pending" ? scheduleMatchBadge(appointment) : ""}
  `;

  const phoneEl = document.querySelector("#apptEditPhone");
  phoneEl.textContent = appointment.patientPhone;
  phoneEl.href = `tel:${appointment.patientPhone.replace(/[^+\d]/g, "")}`;
  document.querySelector("#apptEditService").textContent = appointment.service.title;
  document.querySelector("#apptEditSpecialist").textContent = appointment.specialist.fullName;
  document.querySelector("#apptEditRequested").textContent =
    formatDateAndTime(appointment.requestedDate || appointment.date, appointment.requestedTime || appointment.time);
  document.querySelector("#apptEditConfirmed").textContent = formatDateAndTime(appointment.date, appointment.time);

  const hintEl = document.querySelector("#apptEditScheduleHint");
  if (appointment.status === "pending") {
    if (isAppointmentInSchedule(appointment)) {
      hintEl.className = "schedule-hint ok";
      hintEl.textContent = "Время совпадает с расписанием специалиста — можно подтвердить.";
    } else {
      hintEl.className = "schedule-hint warn";
      hintEl.textContent = `Время вне текущего расписания специалиста - надо связаться по телефону ${appointment.patientPhone}.`;
    }
    hintEl.hidden = false;
  } else {
    hintEl.hidden = true;
  }

  const contactForm = document.querySelector("#apptEditContactForm");
  contactForm.dataset.appointmentContactForm = appointment.id;
  const aContactStatus = appointment.patientContactStatus || "not_contacted";
  document.querySelector("#apptEditContactStatus").innerHTML = Object.entries(appointmentContactStatuses)
    .map(([value, label]) => `<option value="${value}" ${value === aContactStatus ? "selected" : ""}>${label}</option>`)
    .join("");
  document.querySelector("#apptEditContactComment").value = appointment.patientContactComment || "";

  const rescheduleForm = document.querySelector("#apptEditRescheduleForm");
  rescheduleForm.dataset.appointmentRescheduleForm = appointment.id;
  document.querySelector("#apptEditDate").value = appointment.date;
  document.querySelector("#apptEditTime").value = appointment.time;
  document.querySelector("#apptEditComment").value = appointment.comment || "";
  refreshApptEditSpecialistOptions(appointment);

  const saveBtn = document.querySelector("#apptEditSaveBtn");
  saveBtn.dataset.appointmentId = appointment.id;

  dialog.showModal();
}

function refreshApptEditSpecialistOptions(appointment) {
  const select = document.querySelector("#apptEditSpecialistSelect");
  const dateInput = document.querySelector("#apptEditDate");
  const timeInput = document.querySelector("#apptEditTime");
  if (!select || !dateInput || !timeInput) return;

  const eligible = state.specialists.filter(
    (s) => (s.serviceIds || []).includes(appointment.service.id) && s.isActive !== false
  );
  const targetDate = dateInput.value;
  const targetTime = timeInput.value;
  const previousValue = select.value || appointment.specialist.id;

  const options = eligible.map((s) => {
    const windowSlot = state.schedule.find(
      (slot) =>
        slot.isAvailable &&
        slot.specialist?.id === s.id &&
        slot.date === targetDate &&
        slot.startTime <= targetTime &&
        targetTime < slot.endTime
    );
    const isBookedByOther = state.appointments.some(
      (a) =>
        a.id !== appointment.id &&
        a.status !== "cancelled" &&
        a.specialist?.id === s.id &&
        a.date === targetDate &&
        a.time === targetTime
    );

    let suffix = "";
    let disabled = false;
    if (!windowSlot) {
      suffix = " — отсутствует окно";
      disabled = s.id !== appointment.specialist.id;
    } else if (isBookedByOther) {
      suffix = " — занято";
      disabled = s.id !== appointment.specialist.id;
    } else {
      suffix = ` · ${windowSlot.startTime}–${windowSlot.endTime}`;
    }

    const selected = s.id === previousValue ? " selected" : "";
    return `<option value="${s.id}"${selected}${disabled ? " disabled" : ""}>${s.fullName}${suffix}</option>`;
  });
  select.innerHTML = options.join("");
}

const APPOINTMENT_GROUPS = {
  requests: ["pending"],
  booked: ["confirmed", "completed", "cancelled"],
  cancelled: ["cancelled"],
};

function matchesAppointmentFilter(appointment) {
  if (activeStatusFilter === "all") return true;
  const group = APPOINTMENT_GROUPS[activeStatusFilter];
  return group ? group.includes(appointment.status) : appointment.status === activeStatusFilter;
}

function isAppointmentInSchedule(appointment) {
  return state.schedule.some(
    (slot) =>
      slot.isAvailable &&
      slot.specialist?.id === appointment.specialist?.id &&
      slot.date === appointment.date &&
      slot.startTime <= appointment.time &&
      appointment.time < slot.endTime
  );
}

function scheduleMatchBadge(appointment) {
  return isAppointmentInSchedule(appointment)
    ? `<span class="status-badge confirmed"> в расписании</span>`
    : `<span class="status-badge cancelled"> вне расписания</span>`;
}

function appointmentSortAccessor(appointment, key) {
  switch (key) {
    case "phone": return appointment.patientPhone || "";
    case "patient": return appointment.patientName || "";
    case "service": return appointment.service?.title || "";
    case "specialist": return appointment.specialist?.fullName || "";
    case "date": return `${appointment.date || ""}T${appointment.time || ""}`;
    case "status": return appointment.status || "";
    default: return appointment.date || "";
  }
}

function fillAppointmentFilters() {
  const serviceSelect = document.querySelector("#appointmentsServiceFilter");
  const specialistSelect = document.querySelector("#appointmentsSpecialistFilter");
  if (serviceSelect) {
    serviceSelect.innerHTML = `<option value="">Все услуги</option>` + state.services
      .map((service) => `<option value="${service.id}">${service.title}</option>`)
      .join("");
    serviceSelect.value = appointmentFilters.serviceId;
  }
  if (specialistSelect) {
    specialistSelect.innerHTML = `<option value="">Все специалисты</option>` + state.specialists
      .map((specialist) => `<option value="${specialist.id}">${specialist.fullName}</option>`)
      .join("");
    specialistSelect.value = appointmentFilters.specialistId;
  }
}

function renderAppointments() {
  const counts = { all: state.appointments.length, requests: 0, booked: 0, cancelled: 0 };
  state.appointments.forEach((a) => {
    if (a.status === "pending") counts.requests += 1;
    else counts.booked += 1;
    if (a.status === "cancelled") counts.cancelled += 1;
  });
  document.querySelectorAll("[data-count]").forEach((el) => {
    el.textContent = counts[el.dataset.count] ?? 0;
  });

  const filtered = state.appointments.filter((a) => {
    const patientNeedle = appointmentFilters.patient;
    return matchesAppointmentFilter(a) &&
      (!patientNeedle || `${a.patientName}`.toLowerCase().includes(patientNeedle)) &&
      (!appointmentFilters.serviceId || a.service?.id === appointmentFilters.serviceId) &&
      (!appointmentFilters.specialistId || a.specialist?.id === appointmentFilters.specialistId) &&
      (!appointmentFilters.date || a.date === appointmentFilters.date) &&
      matchesSearch("appointments", `${a.patientName} ${a.patientPhone} ${a.service.title} ${a.specialist.fullName}`);
  });
  const sorted = sortRows(filtered, state.appointmentsSort.key, state.appointmentsSort.dir, appointmentSortAccessor);
  const pageRows = paginate("appointments", sorted, "#appointmentsFooter");
  const tbody = document.querySelector("#appointmentsTable");

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td class="empty-row" colspan="7">${
      tablePages.appointments.search ? "По запросу ничего не найдено" : "Записей пока нет"
    }</td></tr>`;
    renderAppointmentDetail();
    return;
  }

  tbody.innerHTML = pageRows
    .map((a) => {
      const nextAction =
        a.status === "pending"
          ? `<button class="status-action" type="button" data-appointment="${a.id}" data-next-status="confirmed">Подтвердить</button>`
          : a.status === "confirmed"
            ? `<button class="status-action" type="button" data-appointment="${a.id}" data-next-status="completed">Завершить</button>`
            : `<button class="status-action" type="button" data-appointment="${a.id}" data-next-status="pending">Вернуть</button>`;

      const cancelAction =
        a.status === "pending" || a.status === "confirmed"
          ? `<button class="status-action danger" type="button" data-appointment="${a.id}" data-next-status="cancelled">Отменить</button>`
          : "";

      return `
        <tr data-row-search="${a.patientName} ${a.patientPhone} ${a.service.title} ${a.specialist.fullName} ${a.appointmentNumber || ""}" data-select-appointment="${a.id}">
          <td><strong>${a.patientName}</strong></td>
          <td>${a.service.title}</td>
          <td>${a.specialist.fullName}</td>
          <td><strong>${formatDateAndTime(a.date, a.time)}</strong></td>
          <td>${statusBadge(a.status, appointmentStatuses)}${a.status === "pending" ? `<br />${scheduleMatchBadge(a)}` : ""}</td>
          <td><div class="table-actions">${nextAction}${cancelAction}</div></td>
        </tr>
      `;
    })
    .join("");

  renderSortIcons("appointments", state.appointmentsSort);
  renderAppointmentDetail();
}

function serviceSortAccessor(s, key) {
  switch (key) {
    case "title": return s.title || "";
    case "category": return s.category?.title || "";
    case "price": return Number(s.price) || 0;
    case "duration": return Number(s.durationMinutes) || 0;
    case "status": return s.isActive ? 1 : 0;
    default: return s.title || "";
  }
}

function renderServices() {
  const filtered = (selectedServiceCategoryId
    ? state.services.filter((s) => s.category.id === selectedServiceCategoryId)
    : state.services
  ).filter((s) => matchesSearch("services", `${s.title} ${s.category.title} ${s.slug}`));
  const visibleServices = sortRows(filtered, state.servicesSort.key, state.servicesSort.dir, serviceSortAccessor);
  const pageRows = paginate("services", visibleServices, "#servicesFooter");
  const tbody = document.querySelector("#servicesTable");
  renderSortIcons("services", state.servicesSort);

  if (visibleServices.length === 0) {
    tbody.innerHTML = `<tr><td class="empty-row" colspan="6">${
      tablePages.services.search ? "По запросу ничего не найдено" : "Услуг пока нет"
    }</td></tr>`;
  } else {
    tbody.innerHTML = pageRows
      .map(
        (s) => `
      <tr data-row-search="${s.title} ${s.category.title} ${s.slug}">
        <td><strong>${s.title}</strong></td>
        <td>${s.category.title}</td>
        <td>${formatMoney(s.price)}</td>
        <td>${s.durationMinutes ?? "—"} мин</td>
        <td>${s.isActive ? statusBadge("confirmed", { confirmed: "Активна" }) : statusBadge("cancelled", { cancelled: "Скрыта" })}</td>
        <td>
          <div class="table-actions">
            <button class="status-action" type="button" data-service-edit="${s.id}">Изменить</button>
            ${s.isActive
              ? `<button class="status-action danger" type="button" data-service-delete="${s.id}">Скрыть</button>`
              : `<button class="status-action" type="button" data-service-restore="${s.id}">Вернуть</button>`}
            <button class="status-action danger" type="button" data-service-hard-delete="${s.id}">Удалить</button>
          </div>
        </td>
      </tr>
    `
      )
      .join("");
  }

  document.querySelector("#serviceCategories").innerHTML = state.serviceCategories
    .map((cat) => {
      const count = state.services.filter((s) => s.category.id === cat.id).length;
      const isActive = cat.id === selectedServiceCategoryId;
      const thumb = cat.imageUrl
        ? `<img class="category-thumb" src="${cat.imageUrl}" alt="" loading="lazy" onerror="this.onerror=null;this.replaceWith(Object.assign(document.createElement('div'),{className:'category-thumb is-empty',textContent:'—'}))" />`
        : `<div class="category-thumb is-empty" aria-hidden="true">—</div>`;
      return `
        <article class="category-item${isActive ? " is-active" : ""}" data-service-category="${cat.id}" title="Клик — показать только услуги категории. Повторный клик — показать все.">
          ${thumb}
          <div class="category-info">
            <strong>${cat.title}</strong>
            ${cat.description ? `<p class="category-desc">${cat.description}</p>` : ""}
          </div>
          <span class="category-count">${count} услуг(и)</span>
          <div class="category-actions">
            <button class="status-action" type="button" data-service-category-edit="${cat.id}">Изменить</button>
            <button class="status-action danger" type="button" data-service-category-delete="${cat.id}">Удалить</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function specialistSortAccessor(s, key) {
  switch (key) {
    case "fullName": return s.fullName || "";
    case "position": return s.position || "";
    case "specialization": return s.specialization || "";
    case "experience": return Number(s.experienceYears) || 0;
    case "status": return s.isActive ? 1 : 0;
    default: return s.fullName || "";
  }
}

function renderSpecialists() {
  const matched = state.specialists.filter((s) =>
    matchesSearch("specialists", `${s.fullName} ${s.position} ${s.specialization}`)
  );
  const filtered = sortRows(matched, state.specialistsSort.key, state.specialistsSort.dir, specialistSortAccessor);
  const pageRows = paginate("specialists", filtered, "#specialistsFooter");
  const tbody = document.querySelector("#specialistsTable");
  renderSortIcons("specialists", state.specialistsSort);

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td class="empty-row" colspan="6">${
      tablePages.specialists.search ? "По запросу ничего не найдено" : "Специалистов пока нет"
    }</td></tr>`;
    return;
  }

  tbody.innerHTML = pageRows
    .map(
      (s) => `
      <tr data-row-search="${s.fullName} ${s.position} ${s.specialization}">
        <td><strong>${s.fullName}</strong></td>
        <td>${s.position}</td>
        <td>${s.specialization}</td>
        <td>${s.experienceYears ?? "—"} лет</td>
        <td>${s.isActive ? statusBadge("confirmed", { confirmed: "Активен" }) : statusBadge("cancelled", { cancelled: "Скрыт" })}</td>
        <td>
          <div class="table-actions">
            <button class="status-action" type="button" data-specialist-edit="${s.id}">Изменить</button>
            ${s.isActive
              ? `<button class="status-action danger" type="button" data-specialist-delete="${s.id}">Скрыть</button>`
              : `<button class="status-action" type="button" data-specialist-restore="${s.id}">Вернуть</button>`}
            <button class="status-action danger" type="button" data-specialist-hard-delete="${s.id}">Удалить</button>
          </div>
        </td>
      </tr>
    `
    )
    .join("");
}

function productSortAccessor(p, key) {
  switch (key) {
    case "title": return p.title;
    case "category": return p.category?.title;
    case "description": return p.description || "";
    case "price": return Number(p.price) || 0;
    case "stock": return Number(p.stock) || 0;
    case "createdAt": return p.createdAt ? new Date(p.createdAt).getTime() : 0;
    case "status": return p.isActive ? 1 : 0;
    default: return p.title;
  }
}

function renderProducts() {
  const needle = tablePages.products.search;
  const filtered = needle
    ? state.products.filter((p) =>
        `${p.title} ${p.category.title} ${p.slug} ${p.description || ""}`.toLowerCase().includes(needle)
      )
    : state.products;
  const sorted = sortRows(filtered, state.productsSort.key, state.productsSort.dir, productSortAccessor);
  const total = sorted.length;
  const page = paginate("products", sorted, "#productsFooter");

  const tbody = document.querySelector("#productsTable");
  if (total === 0) {
    const message = needle ? "По запросу ничего не найдено" : "Товаров пока нет";
    tbody.innerHTML = `<tr><td class="empty-row" colspan="8">${message}</td></tr>`;
  } else {
    tbody.innerHTML = page
      .map((p) => {
        const thumb = p.imageUrl
          ? `<img class="product-thumb" src="${p.imageUrl}" alt="" loading="lazy" />`
          : `<div class="product-thumb is-empty" aria-hidden="true">—</div>`;
        return `
          <tr data-row-search="${p.title} ${p.category.title} ${p.slug}">
            <td>
              <div class="product-cell">
                ${thumb}
                <strong>${p.title}</strong>
              </div>
            </td>
            <td>${p.category.title}</td>
            <td class="desc-cell">${p.description || "—"}</td>
            <td>${formatMoney(p.price)}</td>
            <td>${p.stock} шт.</td>
            <td>${formatDateTime(p.createdAt)}</td>
            <td>${p.isActive ? statusBadge("confirmed", { confirmed: "Активен" }) : statusBadge("cancelled", { cancelled: "Скрыт" })}</td>
            <td>
              <div class="table-actions product-actions">
                <button class="status-action" type="button" data-product-edit="${p.id}">Изменить</button>
                ${p.isActive
                  ? `<button class="status-action" type="button" data-product-delete="${p.id}">Скрыть</button>`
                  : `<button class="status-action" type="button" data-product-restore="${p.id}">Вернуть</button>`}
                <button class="status-action danger" type="button" data-product-hard-delete="${p.id}">Удалить</button>
              </div>
            </td>
          </tr>
        `;
      })
      .join("");
  }
  renderSortIcons("products", state.productsSort);
}

function orderSortAccessor(o, key) {
  switch (key) {
    case "id": return o.orderNumber || o.id;
    case "recipient": return o.recipientName;
    case "totalPrice": return Number(o.totalPrice) || 0;
    case "paymentStatus": return o.paymentStatus;
    case "orderStatus": return o.orderStatus;
    case "createdAt": return o.createdAt ? new Date(o.createdAt).getTime() : 0;
    default: return o.id;
  }
}

function renderOrders() {
  const needle = tablePages.orders.search;
  const filtered = needle
    ? state.orders.filter((o) => {
        const productTitles = (o.items || []).map((item) => item.product?.title || "").join(" ");
        return `${o.orderNumber || ""} ${o.recipientName || ""} ${productTitles}`
          .toLowerCase()
          .includes(needle);
      })
    : state.orders;
  const sorted = sortRows(filtered, state.ordersSort.key, state.ordersSort.dir, orderSortAccessor);
  const total = sorted.length;
  const page = paginate("orders", sorted, "#ordersFooter");

  const tbody = document.querySelector("#ordersTable");
  if (total === 0) {
    const message = needle ? "По запросу ничего не найдено" : "Заказов пока нет";
    tbody.innerHTML = `<tr><td class="empty-row" colspan="8">${message}</td></tr>`;
  } else {
    tbody.innerHTML = page
      .map((o) => {
        const options = Object.entries(orderStatuses)
          .map(
            ([value, label]) =>
              `<option value="${value}" ${o.orderStatus === value ? "selected" : ""}>${label}</option>`,
          )
          .join("");
        const products = (o.items || []).length
          ? o.items
              .map((item) => {
                const quantity = Number(item.quantity) > 1 ? ` <b>×${item.quantity}</b>` : "";
                return `<span>${item.product?.title || "Товар удалён"}${quantity}</span>`;
              })
              .join("")
          : "—";
        return `
          <tr data-row-search="${o.orderNumber || ""} ${o.recipientName || ""} ${o.recipientPhone || ""} ${(o.items || []).map((item) => item.product?.title || "").join(" ")}">
            <td><strong>${o.orderNumber || "—"}</strong></td>
            <td>${formatDateTime(o.createdAt)}</td>
            <td>${o.recipientName || "—"}</td>
            <td><div class="order-products-cell">${products}</div></td>
            <td>${deliveryMethods[o.deliveryMethod] || "—"}</td>
            <td>${formatMoney(o.totalPrice)}</td>
            <td>${statusBadge(o.paymentStatus, paymentStatuses)}<small class="cell-sub">${paymentMethods[o.paymentMethod] || ""}</small></td>
            <td>
              <select class="status-select status-${o.orderStatus}" data-order-status="${o.id}" aria-label="Изменить статус заказа">${options}</select>
            </td>
          </tr>
        `;
      })
      .join("");
  }
  renderSortIcons("orders", state.ordersSort);
}

function userSortAccessor(u, key) {
  switch (key) {
    case "fullName": return u.fullName || "";
    case "phone": return u.phone || "";
    case "email": return u.email || "";
    case "role": return u.role || "";
    case "createdAt": return u.createdAt ? new Date(u.createdAt).getTime() : 0;
    default: return u.fullName || "";
  }
}

function renderUsers() {
  const matched = state.users
    .filter((u) => activeUserRole === "all" || u.role === activeUserRole)
    .filter((u) => matchesSearch("users", `${u.fullName} ${u.phone} ${u.email || ""} ${u.role}`));
  const filtered = sortRows(matched, state.usersSort.key, state.usersSort.dir, userSortAccessor);
  const pageRows = paginate("users", filtered, "#usersFooter");
  const tbody = document.querySelector("#usersTable");
  renderSortIcons("users", state.usersSort);

  if (filtered.length === 0) {
    const emptyLabels = {
      all: "Пользователей пока нет",
      patient: "Пациентов пока нет",
      doctor: "Врачей пока нет",
      admin: "Администраторов пока нет",
    };
    tbody.innerHTML = `<tr><td class="empty-row" colspan="6">${
      tablePages.users.search ? "По запросу ничего не найдено" : emptyLabels[activeUserRole]
    }</td></tr>`;
    return;
  }

  tbody.innerHTML = pageRows
    .map(
      (u) => `
      <tr data-row-search="${u.fullName} ${u.phone} ${u.email || ""} ${u.role}">
        <td><strong>${u.fullName}</strong></td>
        <td>${u.phone}</td>
        <td>${u.email || "—"}</td>
        <td><span class="role-badge ${u.role}">${u.role}</span></td>
        <td>${formatDate(u.createdAt)}</td>
        <td>
          <div class="table-actions">
            <button class="status-action" type="button" data-user-edit="${u.id}">Изменить</button>
            <button class="status-action danger" type="button" data-user-delete="${u.id}">Удалить</button>
          </div>
        </td>
      </tr>
    `
    )
    .join("");

}

function renderStars(rating) {
  const r = Math.max(0, Math.min(5, Math.round(rating)));
  return "★".repeat(r) + "☆".repeat(5 - r);
}

function reviewSortAccessor(r, key) {
  switch (key) {
    case "author": return r.authorName || "";
    case "rating": return Number(r.rating) || 0;
    case "content": return r.text || "";
    case "status": return r.isPublished ? 1 : 0;
    default: return r.authorName || "";
  }
}

function renderReviews() {
  const filterFn = (r) => {
    if (activeReviewFilter === "archived") return !r.isPublished;
    if (activeReviewFilter === "published") return r.isPublished;
    return true;
  };
  const matched = state.reviews
    .filter(filterFn)
    .filter((r) => matchesSearch("reviews", `${r.authorName} ${r.text}`));
  const filtered = sortRows(matched, state.reviewsSort.key, state.reviewsSort.dir, reviewSortAccessor);
  const pageRows = paginate("reviews", filtered, "#reviewsFooter");
  const tbody = document.querySelector("#reviewsTable");
  if (!tbody) return;
  renderSortIcons("reviews", state.reviewsSort);

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td class="empty-row" colspan="5">${
      tablePages.reviews.search ? "По запросу ничего не найдено" : "Отзывов пока нет"
    }</td></tr>`;
    return;
  }

  tbody.innerHTML = pageRows
    .map((r) => {
      const preview = r.text.length > 140 ? r.text.slice(0, 140) + "…" : r.text;
      const toggleLabel = r.isPublished ? "Архивировать" : "Опубликовать";
      const statusBadge = r.isPublished
        ? `<span class="review-status published">Опубликован</span>`
        : `<span class="review-status pending">Архивирован</span>`;
      return `
        <tr data-row-search="${r.authorName} ${r.text}">
          <td><strong>${r.authorName}</strong></td>
          <td><span class="review-stars">${renderStars(r.rating)}</span></td>
          <td class="review-text-cell">${preview}</td>
          <td>${statusBadge}</td>
          <td>
            <div class="table-actions">
              <button class="status-action" type="button" data-review-toggle="${r.id}" data-review-target="${r.isPublished ? "false" : "true"}">${toggleLabel}</button>
              <button class="status-action danger" type="button" data-review-delete="${r.id}">Удалить</button>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function fillReviewForm(rev = null) {
  const form = document.querySelector("#reviewForm");
  form.reset();
  form.elements.id.value = rev?.id || "";
  form.elements.authorName.value = rev?.authorName || "";
  form.elements.rating.value = String(rev?.rating ?? 5);
  form.elements.text.value = rev?.text || "";
  form.elements.sortOrder.value = rev?.sortOrder ?? 0;
  form.elements.isPublished.checked = rev ? Boolean(rev.isPublished) : true;
  document.querySelector("#reviewDialogTitle").textContent =
    rev ? "Редактировать отзыв" : "Добавить отзыв";
}

function getReviewPayload(form) {
  return {
    authorName: form.elements.authorName.value.trim(),
    rating: Number(form.elements.rating.value),
    text: form.elements.text.value.trim(),
    sortOrder: Number(form.elements.sortOrder.value) || 0,
    isPublished: form.elements.isPublished.checked,
  };
}

function fillDialogSelects() {
  syncAppointmentSelects("service");
  const doctorOptions = state.users
    .filter((u) => u.role === "doctor")
    .map((u) => `<option value="${u.id}">${u.fullName} (${u.phone})</option>`)
    .join("");
  document.querySelector("#specialistUserId").innerHTML =
    `<option value="">Не привязан</option>` + doctorOptions;
  document.querySelector("#scheduleSpecialist").innerHTML = state.specialists
    .filter((s) => s.isActive)
    .map((s) => `<option value="${s.id}">${s.fullName}</option>`)
    .join("");
  document.querySelector("#serviceCategorySelect").innerHTML = state.serviceCategories
    .map((category) => `<option value="${category.id}">${category.title}</option>`)
    .join("");
  document.querySelector("#specialistSpecialization").innerHTML = state.serviceCategories
    .map((category) => `<option value="${category.title}">${category.title}</option>`)
    .join("");
  renderSpecialistServiceOptions(document.querySelector("#specialistSpecialization").value);
  document.querySelector("#productCategorySelect").innerHTML = state.productCategories
    .map((category) => `<option value="${category.id}">${category.title}</option>`)
    .join("");
  document.querySelector("#orderUserId").innerHTML =
    `<option value="">Выберите покупателя</option>` +
    state.users
      .filter((u) => u.role === "patient")
      .map((u) => `<option value="${u.id}">${u.fullName} (${u.phone})</option>`)
      .join("");
}

function orderProductOptions() {
  return (
    `<option value="">Выберите товар</option>` +
    state.products
      .filter((p) => p.isActive)
      .map((p) => `<option value="${p.id}">${p.title} — ${formatMoney(p.price)}</option>`)
      .join("")
  );
}

function addOrderItemRow() {
  const container = document.querySelector("#orderItemsContainer");
  const row = document.createElement("div");
  row.className = "order-item-row";
  row.innerHTML = `
    <select class="order-item-product" required>${orderProductOptions()}</select>
    <input class="order-item-qty" type="number" min="1" step="1" value="1" required />
    <button class="status-action danger" type="button" data-order-item-remove>×</button>
  `;
  container.appendChild(row);
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("is-visible");
  window.setTimeout(() => toast.classList.remove("is-visible"), 2400);
}

function optionalText(value) {
  const trimmed = String(value || "").trim();
  return trimmed.length > 0 ? trimmed : null;
}

function optionalNumber(value) {
  return value === "" || value == null ? null : Number(value);
}

function setSelectedOptions(select, values) {
  const selected = new Set(values || []);
  Array.from(select.options).forEach((option) => {
    option.selected = selected.has(option.value);
  });
}

function renderSelectOptions(select, items, selectedValue, getLabel, emptyLabel) {
  if (items.length === 0) {
    select.innerHTML = `<option value="" disabled>${emptyLabel}</option>`;
    return "";
  }

  select.innerHTML = items.map((item) => `<option value="${item.id}">${getLabel(item)}</option>`).join("");
  if (selectedValue && items.some((item) => item.id === selectedValue)) {
    select.value = selectedValue;
  }
  return select.value;
}

function activeAppointmentServices(specialistId = "") {
  const services = state.services.filter((service) => service.isActive);
  if (!specialistId) return services;
  const specialist = state.specialists.find((item) => item.id === specialistId);
  if (!specialist) return services;
  return services.filter((service) => (specialist.serviceIds || []).includes(service.id));
}

function activeAppointmentSpecialists(serviceId = "") {
  const specialists = state.specialists.filter((specialist) => specialist.isActive);
  if (!serviceId) return specialists;
  return specialists.filter((specialist) => (specialist.serviceIds || []).includes(serviceId));
}

function syncAppointmentSelects(changedField = "service") {
  const serviceSelect = document.querySelector("#appointmentService");
  const specialistSelect = document.querySelector("#appointmentSpecialist");
  const currentServiceId = serviceSelect.value;
  const currentSpecialistId = specialistSelect.value;

  if (changedField === "specialist") {
    const specialistId = renderSelectOptions(
      specialistSelect,
      activeAppointmentSpecialists(),
      currentSpecialistId,
      (specialist) => specialist.fullName,
      "Нет активных специалистов"
    );
    renderSelectOptions(
      serviceSelect,
      activeAppointmentServices(specialistId),
      currentServiceId,
      (service) => service.title,
      "Нет услуг для выбранного специалиста"
    );
    return;
  }

  const serviceId = renderSelectOptions(
    serviceSelect,
    activeAppointmentServices(),
    currentServiceId,
    (service) => service.title,
    "Нет активных услуг"
  );
  renderSelectOptions(
    specialistSelect,
    activeAppointmentSpecialists(serviceId),
    currentSpecialistId,
    (specialist) => specialist.fullName,
    "Нет специалистов для выбранной услуги"
  );
}

function renderSpecialistServiceOptions(specialization, selectedServiceIds = []) {
  const select = document.querySelector("#specialistServiceIds");
  const choices = document.querySelector("#specialistServiceChoices");
  const selected = new Set(selectedServiceIds || []);
  const services = state.services.filter(
    (service) =>
      service.isActive &&
      (service.category?.title === specialization || selected.has(service.id))
  );

  select.innerHTML =
    services.length > 0
      ? services
          .map((service) => `<option value="${service.id}">${service.title}</option>`)
          .join("")
      : `<option value="" disabled>Нет услуг для выбранной специализации</option>`;

  setSelectedOptions(select, selectedServiceIds);

  choices.innerHTML = services.length
    ? services
        .map(
          (service) => `
            <label class="service-choice">
              <input type="checkbox" value="${service.id}" ${selected.has(service.id) ? "checked" : ""} />
              <span>${service.title}</span>
            </label>
          `
        )
        .join("")
    : `<span class="service-choice-empty">Нет услуг для выбранной специализации</span>`;

  choices.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const option = Array.from(select.options).find((item) => item.value === checkbox.value);
      if (option) option.selected = checkbox.checked;
    });
  });
}

function fillSpecialistForm(specialist = null) {
  const form = document.querySelector("#specialistForm");
  form.reset();
  form.elements.id.value = specialist?.id || "";
  form.elements.fullName.value = specialist?.fullName || "";
  form.elements.position.value = specialist?.position || "";
  form.elements.specialization.value = specialist?.specialization || "";
  form.elements.experienceYears.value = specialist?.experienceYears ?? "";
  form.elements.userId.value = specialist?.userId || "";
  form.elements.photoUrl.value = specialist?.photoUrl || "";
  form.elements.isActive.checked = specialist?.isActive ?? true;
  renderSpecialistServiceOptions(form.elements.specialization.value, specialist?.serviceIds || []);
  document.querySelector("#specialistDialogTitle").textContent = specialist ? "Редактировать врача" : "Добавить врача";
}

function getSpecialistPayload(form) {
  return {
    userId: optionalText(form.elements.userId.value),
    fullName: form.elements.fullName.value.trim(),
    position: form.elements.position.value.trim(),
    specialization: form.elements.specialization.value.trim(),
    experienceYears: optionalNumber(form.elements.experienceYears.value),
    photoUrl: optionalText(form.elements.photoUrl.value),
    serviceIds: Array.from(document.querySelector("#specialistServiceIds").selectedOptions).map((o) => o.value),
    isActive: form.elements.isActive.checked,
  };
}

function fillServiceCategoryForm(category = null) {
  const form = document.querySelector("#serviceCategoryForm");
  form.reset();
  form.elements.id.value = category?.id || "";
  form.elements.title.value = category?.title || "";
  form.elements.slug.value = category?.slug || "";
  form.elements.slug.dataset.userEdited = category ? "true" : "";
  form.elements.imageUrl.value = category?.imageUrl || "";
  form.elements.description.value = category?.description || "";
  document.querySelector("#serviceCategoryDialogTitle").textContent =
    category ? "Редактировать категорию" : "Добавить категорию";
}

function fillServiceForm(service = null) {
  const form = document.querySelector("#serviceForm");
  form.reset();
  form.elements.id.value = service?.id || "";
  form.elements.title.value = service?.title || "";
  form.elements.slug.value = service?.slug || "";
  form.elements.slug.dataset.userEdited = service ? "true" : "";
  form.elements.categoryId.value = service?.category?.id || state.serviceCategories[0]?.id || "";
  form.elements.price.value = service?.price ?? "";
  form.elements.durationMinutes.value = service?.durationMinutes ?? "";
  form.elements.imageUrl.value = service?.imageUrl || "";
  form.elements.description.value = service?.description || "";
  form.elements.contraindications.value = service?.contraindications || "";
  form.elements.isActive.checked = service?.isActive ?? true;
  document.querySelector("#serviceDialogTitle").textContent = service ? "Редактировать услугу" : "Добавить услугу";
}

function getServicePayload(form) {
  return {
    categoryId: form.elements.categoryId.value,
    title: form.elements.title.value.trim(),
    slug: form.elements.slug.value.trim(),
    description: form.elements.description.value.trim(),
    price: Number(form.elements.price.value),
    durationMinutes: optionalNumber(form.elements.durationMinutes.value),
    imageUrl: optionalText(form.elements.imageUrl.value),
    contraindications: optionalText(form.elements.contraindications.value),
    isActive: form.elements.isActive.checked,
  };
}

function fillProductForm(product = null) {
  const form = document.querySelector("#productForm");
  form.reset();
  form.elements.id.value = product?.id || "";
  form.elements.title.value = product?.title || "";
  form.elements.slug.value = product?.slug || "";
  form.elements.slug.dataset.userEdited = product ? "true" : "";
  form.elements.categoryId.value = product?.category?.id || state.productCategories[0]?.id || "";
  form.elements.price.value = product?.price ?? "";
  form.elements.stock.value = product?.stock ?? "";
  form.elements.imageUrl.value = product?.imageUrl || "";
  form.elements.description.value = product?.description || "";
  form.elements.isActive.checked = product?.isActive ?? true;
  document.querySelector("#productDialogTitle").textContent = product ? "Редактировать товар" : "Добавить товар";
}

function getProductPayload(form) {
  return {
    categoryId: form.elements.categoryId.value,
    title: form.elements.title.value.trim(),
    slug: form.elements.slug.value.trim(),
    description: form.elements.description.value.trim(),
    price: Number(form.elements.price.value),
    imageUrl: optionalText(form.elements.imageUrl.value),
    stock: Number(form.elements.stock.value),
    isActive: form.elements.isActive.checked,
  };
}

function fillScheduleForm(schedule = null) {
  const form = document.querySelector("#scheduleForm");
  form.reset();
  form.elements.id.value = schedule?.id || "";
  form.elements.specialistId.value = schedule?.specialist?.id || state.specialists[0]?.id || "";
  form.elements.date.value = schedule?.date || "";
  form.elements.startTime.value = schedule?.startTime || "";
  form.elements.endTime.value = schedule?.endTime || "";
  form.elements.isAvailable.checked = schedule?.isAvailable ?? true;
  document.querySelector("#scheduleDialogTitle").textContent = schedule ? "Редактировать окно записи" : "Добавить окно записи";
}

function getSchedulePayload(form) {
  return {
    specialistId: form.elements.specialistId.value,
    date: form.elements.date.value,
    startTime: form.elements.startTime.value,
    endTime: form.elements.endTime.value,
    isAvailable: form.elements.isAvailable.checked,
  };
}

function fillUserForm(user = null) {
  const form = document.querySelector("#userForm");
  const passwordField = document.querySelector("#userPasswordField");
  const passwordLabel = document.querySelector("#userPasswordLabel");
  form.reset();
  form.elements.id.value = user?.id || "";
  form.elements.fullName.value = user?.fullName || "";
  form.elements.phone.value = user?.phone || "";
  form.elements.email.value = user?.email || "";
  form.elements.role.value = user?.role || "patient";
  form.elements.password.value = "";
  form.elements.password.required = !user;
  passwordField.style.display = "";
  passwordLabel.textContent = user ? "Новый пароль" : "Пароль";
  form.elements.password.placeholder = user ? "Оставьте пустым, чтобы не менять" : "Минимум 8 символов";
  document.querySelector("#userDialogTitle").textContent = user ? "Редактировать пользователя" : "Добавить пользователя";
}

function getUserPayload(form, isEdit) {
  const payload = {
    fullName: form.elements.fullName.value.trim(),
    phone: form.elements.phone.value.trim(),
    email: optionalText(form.elements.email.value),
    role: form.elements.role.value,
  };
  if (!isEdit) {
    payload.password = form.elements.password.value;
  } else if (optionalText(form.elements.password.value)) {
    payload.password = form.elements.password.value;
  }
  return payload;
}

function switchPanel(panelId) {
  currentPanel = panelId;
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("is-active", panel.id === panelId);
  });
  document.querySelectorAll(".nav-item[data-panel]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.panel === panelId);
  });
  document.querySelector("#globalSearch").value = "";
  const productsSearch = document.querySelector("#productsSearch");
  if (productsSearch) productsSearch.value = "";
  const ordersSearch = document.querySelector("#ordersSearch");
  if (ordersSearch) ordersSearch.value = "";
  Object.values(tablePages).forEach((p) => {
    p.search = "";
    p.page = 1;
  });
  const scope = PANEL_TO_SCOPE[panelId];
  if (scope) renderScope(scope);
}

function applySearch(query) {
  const normalized = query.trim().toLowerCase();
  const scope = PANEL_TO_SCOPE[currentPanel];
  if (!scope) return;
  tablePages[scope].search = normalized;
  tablePages[scope].page = 1;
  renderScope(scope);
}

function renderAll() {
  renderMetrics();
  renderPriorityList();
  renderSchedule();
  renderAppointments();
  renderServices();
  renderSpecialists();
  renderProducts();
  renderOrders();
  renderUsers();
  fillDialogSelects();
  fillAppointmentFilters();
  renderReviews();
  renderPendingNotification();
}

function renderPendingNotification() {
  const countEl = document.querySelector("#sidebarPendingCount");
  if (!countEl) return;
  const pending = state.appointments.filter((a) => a.status === "pending");
  countEl.textContent = pending.length;
  const widget = document.querySelector("#appointmentsNotification");
  widget?.classList.toggle("has-pending", pending.length > 0);
}

function activateSpecTab(target) {
  document.querySelectorAll(".tab[data-spec-tab]").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.specTab === target);
  });
  document.querySelectorAll(".tab-panel[data-spec-tab]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.specTab === target);
  });
  document
    .querySelectorAll("#specialists .header-actions [data-spec-tab]")
    .forEach((btn) => {
      btn.hidden = btn.dataset.specTab !== target;
    });
}

function activateServicesTab(target) {
  document.querySelectorAll("#services .tab[data-svc-tab]").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.svcTab === target);
  });
  document.querySelectorAll("#services .tab-panel[data-svc-tab]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.svcTab === target);
  });
  document.querySelectorAll("#services .header-actions [data-svc-tab]").forEach((btn) => {
    btn.hidden = btn.dataset.svcTab !== target;
  });
}

function bindEvents() {
  // Перестраиваем список «Новый специалист», когда меняют дату/время в форме переноса.
  const refreshOnTimeChange = () => {
    const rescheduleForm = document.querySelector("#apptEditRescheduleForm");
    const appointmentId = rescheduleForm?.dataset.appointmentRescheduleForm;
    if (!appointmentId) return;
    const appointment = state.appointments.find((a) => a.id === appointmentId);
    if (appointment) refreshApptEditSpecialistOptions(appointment);
  };
  document.querySelector("#apptEditDate")?.addEventListener("change", refreshOnTimeChange);
  document.querySelector("#apptEditTime")?.addEventListener("change", refreshOnTimeChange);

  const appointmentsTable = document.querySelector("#appointmentsTable");
  if (appointmentsTable) {
    let lastHoveredAppointmentId = null;
    appointmentsTable.addEventListener("mouseover", (e) => {
      const row = e.target.closest("[data-select-appointment]");
      if (!row) return;
      const id = row.dataset.selectAppointment;
      if (id === lastHoveredAppointmentId) return;
      lastHoveredAppointmentId = id;
      renderAppointmentDetail(id);
    });
  }

  document.querySelectorAll(".nav-item[data-panel]").forEach((button) => {
    button.addEventListener("click", () => switchPanel(button.dataset.panel));
  });

  document.querySelectorAll(".tab[data-spec-tab]").forEach((tab) => {
    tab.addEventListener("click", () => activateSpecTab(tab.dataset.specTab));
  });

  document.querySelectorAll("#services .tab[data-svc-tab]").forEach((tab) => {
    tab.addEventListener("click", () => activateServicesTab(tab.dataset.svcTab));
  });

  document.querySelector("#schedulePrevWeek")?.addEventListener("click", () => {
    scheduleMonthDate = new Date(scheduleMonthDate.getFullYear(), scheduleMonthDate.getMonth() - 1, 1);
    renderScheduleWeek();
  });
  document.querySelector("#scheduleNextWeek")?.addEventListener("click", () => {
    scheduleMonthDate = new Date(scheduleMonthDate.getFullYear(), scheduleMonthDate.getMonth() + 1, 1);
    renderScheduleWeek();
  });
  document.querySelector("#scheduleTodayWeek")?.addEventListener("click", () => {
    const today = new Date();
    scheduleMonthDate = new Date(today.getFullYear(), today.getMonth(), 1);
    renderScheduleWeek();
  });

  populateSettingsForm();
  document.querySelectorAll("[data-settings-save]").forEach((button) => {
    button.addEventListener("click", saveSettings);
  });
  document.querySelectorAll("[data-settings-reset]").forEach((button) => {
    button.addEventListener("click", resetSettings);
  });
  bindLicenseUploader();

  document.querySelectorAll("[data-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      switchPanel(button.dataset.jump);
      if (button.dataset.jump === "specialists" && button.dataset.jumpTab) {
        activateSpecTab(button.dataset.jumpTab);
      }
      if (button.dataset.jump === "appointments" && button.dataset.jumpTab) {
        activeStatusFilter = button.dataset.jumpTab;
        document.querySelectorAll("[data-status-filter]").forEach((b) => b.classList.remove("is-active"));
        const targetBtn = document.querySelector(`[data-status-filter="${button.dataset.jumpTab}"]`);
        if (targetBtn) targetBtn.classList.add("is-active");
        renderAppointments();
      }
    });
  });

  document.querySelector("#globalSearch").addEventListener("input", (e) => applySearch(e.target.value));

  document.querySelector("#productsSearch")?.addEventListener("input", (e) => {
    tablePages.products.search = e.target.value.trim().toLowerCase();
    tablePages.products.page = 1;
    renderProducts();
  });

  document.querySelector("#ordersSearch")?.addEventListener("input", (e) => {
    tablePages.orders.search = e.target.value.trim().toLowerCase();
    tablePages.orders.page = 1;
    renderOrders();
  });

  document.querySelector("#appointmentsPatientFilter")?.addEventListener("input", (e) => {
    appointmentFilters.patient = e.target.value.trim().toLowerCase();
    tablePages.appointments.page = 1;
    renderAppointments();
  });

  document.querySelector("#appointmentsServiceFilter")?.addEventListener("change", (e) => {
    appointmentFilters.serviceId = e.target.value;
    tablePages.appointments.page = 1;
    renderAppointments();
  });

  document.querySelector("#appointmentsSpecialistFilter")?.addEventListener("change", (e) => {
    appointmentFilters.specialistId = e.target.value;
    tablePages.appointments.page = 1;
    renderAppointments();
  });

  document.querySelector("#appointmentsDateFilter")?.addEventListener("change", (e) => {
    appointmentFilters.date = e.target.value;
    tablePages.appointments.page = 1;
    renderAppointments();
  });

  document.querySelectorAll("[data-status-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      activeStatusFilter = button.dataset.statusFilter;
      document.querySelectorAll("[data-status-filter]").forEach((b) => b.classList.remove("is-active"));
      button.classList.add("is-active");
      renderAppointments();
    });
  });

  // Sortable headers (все таблицы) и пагинация
  document.addEventListener("click", (e) => {
    const SORT_SCOPES = ["appointments", "products", "orders", "services", "specialists", "users", "reviews"];
    const selector = SORT_SCOPES.map((s) => `[data-sort-${s}]`).join(", ");
    const sortHeader = e.target.closest(selector);
    if (sortHeader) {
      const scope = SORT_SCOPES.find(
        (s) => `sort${s.charAt(0).toUpperCase()}${s.slice(1)}` in sortHeader.dataset
      );
      if (!scope) return;
      const key = sortHeader.dataset[`sort${scope.charAt(0).toUpperCase()}${scope.slice(1)}`];
      const sortState = state[`${scope}Sort`];
      if (sortState.key === key) {
        sortState.dir = sortState.dir === "asc" ? "desc" : "asc";
      } else {
        sortState.key = key;
        sortState.dir = "asc";
      }
      renderScope(scope);
      return;
    }

    const pagBtn = e.target.closest("[data-pagination]");
    if (pagBtn) {
      const st = tablePages[pagBtn.dataset.pagination];
      if (!st) return;
      if (pagBtn.dataset.paginationDir === "prev") st.page -= 1;
      if (pagBtn.dataset.paginationDir === "next") st.page += 1;
      renderScope(pagBtn.dataset.pagination); // paginate() сам ограничит page
    }
  });

  document.addEventListener("change", (e) => {
    const sizeSel = e.target.closest("[data-pagination-size]");
    if (!sizeSel) return;
    const scope = sizeSel.dataset.paginationSize;
    const st = tablePages[scope];
    if (!st) return;
    st.perPage = Number(sizeSel.value) || DEFAULT_PER_PAGE;
    st.page = 1;
    renderScope(scope);
  });

  document.addEventListener("change", async (e) => {
    const statusSelect = e.target.closest("[data-order-status]");
    if (!statusSelect) return;
    const orderId = statusSelect.dataset.orderStatus;
    const newStatus = statusSelect.value;
    statusSelect.disabled = true;
    try {
      await apiFetch(`/admin/orders/${orderId}`, {
        method: "PATCH",
        body: JSON.stringify({ orderStatus: newStatus }),
      });
      await loadAll();
      renderAll();
      showToast("Статус заказа обновлён");
    } catch (err) {
      statusSelect.disabled = false;
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.addEventListener("click", async (e) => {
    const categoryEditBtn = e.target.closest("[data-service-category-edit]");
    if (categoryEditBtn) {
      const category = state.serviceCategories.find(
        (c) => c.id === categoryEditBtn.dataset.serviceCategoryEdit
      );
      if (category) {
        fillServiceCategoryForm(category);
        document.querySelector("#serviceCategoryDialog").showModal();
      }
      return;
    }

    const categoryDeleteBtn = e.target.closest("[data-service-category-delete]");
    if (categoryDeleteBtn) {
      const id = categoryDeleteBtn.dataset.serviceCategoryDelete;
      const category = state.serviceCategories.find((c) => c.id === id);
      if (!window.confirm(`Удалить категорию «${category?.title || ""}»?`)) return;
      try {
        await apiFetch(`/admin/service-categories/${id}`, { method: "DELETE" });
        if (selectedServiceCategoryId === id) selectedServiceCategoryId = null;
        await loadAll();
        renderAll();
        showToast("Категория удалена");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const serviceCategoryItem = e.target.closest("[data-service-category]");
    if (serviceCategoryItem) {
      const clickedId = serviceCategoryItem.dataset.serviceCategory;
      const wasSelected = selectedServiceCategoryId === clickedId;
      selectedServiceCategoryId = wasSelected ? null : clickedId;
      tablePages.services.page = 1;
      renderServices();
      if (!wasSelected) activateServicesTab("services");
      return;
    }

    const orderItemRemove = e.target.closest("[data-order-item-remove]");
    if (orderItemRemove) {
      const container = document.querySelector("#orderItemsContainer");
      if (container.querySelectorAll(".order-item-row").length > 1) {
        orderItemRemove.closest(".order-item-row").remove();
      } else {
        showToast("В заказе должна быть хотя бы одна позиция");
      }
      return;
    }

    const statusButton = e.target.closest("[data-appointment]");
    if (statusButton) {
      selectedAppointmentId = statusButton.dataset.appointment;
      try {
        await apiFetch(`/admin/appointments/${statusButton.dataset.appointment}`, {
          method: "PATCH",
          body: JSON.stringify({ status: statusButton.dataset.nextStatus }),
        });
        await loadAll();
        renderAll();
        showToast("Статус записи обновлён");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const row = e.target.closest("[data-select-appointment]");
    if (row && !e.target.closest("button")) {
      selectedAppointmentId = row.dataset.selectAppointment;
      renderAppointmentDetail();
      openAppointmentEditDialog(selectedAppointmentId);
      return;
    }

    if (e.target.closest("[data-appt-edit-close]")) {
      document.querySelector("#appointmentEditDialog").close();
      return;
    }

    const saveApptBtn = e.target.closest("#apptEditSaveBtn");
    if (saveApptBtn && !saveApptBtn.disabled) {
      const appointmentId = saveApptBtn.dataset.appointmentId;
      if (!appointmentId) return;
      const contactForm = document.querySelector("#apptEditContactForm");
      const rescheduleForm = document.querySelector("#apptEditRescheduleForm");
      const contactFd = new FormData(contactForm);
      const rescheduleFd = new FormData(rescheduleForm);
      saveApptBtn.disabled = true;
      try {
        await Promise.all([
          apiFetch(`/admin/appointments/${appointmentId}/contact`, {
            method: "PATCH",
            body: JSON.stringify({
              patientContactStatus: contactFd.get("patientContactStatus"),
              patientContactComment: contactFd.get("patientContactComment") || null,
            }),
          }),
          apiFetch(`/admin/appointments/${appointmentId}/reschedule`, {
            method: "PATCH",
            body: JSON.stringify({
              specialistId: rescheduleFd.get("specialistId"),
              date: rescheduleFd.get("date"),
              time: rescheduleFd.get("time"),
              comment: rescheduleFd.get("comment") || null,
            }),
          }),
        ]);
        document.querySelector("#appointmentEditDialog").close();
        await loadAll();
        renderAll();
        showToast("Изменения сохранены");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      } finally {
        saveApptBtn.disabled = false;
      }
      return;
    }


    const specialistEditButton = e.target.closest("[data-specialist-edit]");
    if (specialistEditButton) {
      const specialist = state.specialists.find((item) => item.id === specialistEditButton.dataset.specialistEdit);
      if (specialist) {
        fillSpecialistForm(specialist);
        document.querySelector("#specialistDialog").showModal();
      }
      return;
    }

    const specialistDeleteButton = e.target.closest("[data-specialist-delete]");
    if (specialistDeleteButton) {
      if (!window.confirm("Скрыть этого специалиста из каталога?")) return;
      try {
        await apiFetch(`/admin/specialists/${specialistDeleteButton.dataset.specialistDelete}`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Специалист скрыт");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const specialistRestoreButton = e.target.closest("[data-specialist-restore]");
    if (specialistRestoreButton) {
      try {
        await apiFetch(`/admin/specialists/${specialistRestoreButton.dataset.specialistRestore}`, {
          method: "PATCH",
          body: JSON.stringify({ isActive: true }),
        });
        await loadAll();
        renderAll();
        showToast("Специалист возвращён в каталог");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const specialistHardDeleteButton = e.target.closest("[data-specialist-hard-delete]");
    if (specialistHardDeleteButton) {
      if (!window.confirm("Полностью удалить этого специалиста из базы? Действие необратимо.")) return;
      try {
        await apiFetch(`/admin/specialists/${specialistHardDeleteButton.dataset.specialistHardDelete}/hard`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Специалист удалён");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const scheduleEditButton = e.target.closest("[data-schedule-edit]");
    if (scheduleEditButton) {
      const schedule = state.schedule.find((item) => item.id === scheduleEditButton.dataset.scheduleEdit);
      if (schedule) {
        fillScheduleForm(schedule);
        document.querySelector("#scheduleDialog").showModal();
      }
      return;
    }

    const scheduleDeleteButton = e.target.closest("[data-schedule-delete]");
    if (scheduleDeleteButton) {
      if (!window.confirm("Скрыть это окно записи?")) return;
      try {
        await apiFetch(`/admin/doctor-schedule/${scheduleDeleteButton.dataset.scheduleDelete}`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Окно записи скрыто");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const scheduleRestoreButton = e.target.closest("[data-schedule-restore]");
    if (scheduleRestoreButton) {
      try {
        await apiFetch(`/admin/doctor-schedule/${scheduleRestoreButton.dataset.scheduleRestore}`, {
          method: "PATCH",
          body: JSON.stringify({ isAvailable: true }),
        });
        await loadAll();
        renderAll();
        showToast("Окно записи возвращено");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const scheduleHardDeleteButton = e.target.closest("[data-schedule-hard-delete]");
    if (scheduleHardDeleteButton) {
      if (!window.confirm("Полностью удалить это окно записи? Действие необратимо.")) return;
      try {
        await apiFetch(`/admin/doctor-schedule/${scheduleHardDeleteButton.dataset.scheduleHardDelete}/hard`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Окно записи удалено");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const userEditButton = e.target.closest("[data-user-edit]");
    if (userEditButton) {
      const user = state.users.find((item) => item.id === userEditButton.dataset.userEdit);
      if (user) {
        fillUserForm(user);
        document.querySelector("#userDialog").showModal();
      }
      return;
    }

    const userDeleteButton = e.target.closest("[data-user-delete]");
    if (userDeleteButton) {
      if (!window.confirm("Удалить этого пользователя?")) return;
      try {
        await apiFetch(`/admin/users/${userDeleteButton.dataset.userDelete}`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Пользователь удалён");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const reviewToggleButton = e.target.closest("[data-review-toggle]");
    if (reviewToggleButton) {
      const id = reviewToggleButton.dataset.reviewToggle;
      const nextPublished = reviewToggleButton.dataset.reviewTarget === "true";
      try {
        await apiFetch(`/admin/reviews/${id}`, {
          method: "PATCH",
          body: JSON.stringify({ isPublished: nextPublished }),
        });
        await loadAll();
        renderAll();
        showToast(nextPublished ? "Отзыв опубликован" : "Отзыв архивирован");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const reviewDeleteButton = e.target.closest("[data-review-delete]");
    if (reviewDeleteButton) {
      if (!window.confirm("Удалить этот отзыв?")) return;
      try {
        await apiFetch(`/admin/reviews/${reviewDeleteButton.dataset.reviewDelete}`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Отзыв удалён");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const reviewFilterButton = e.target.closest("[data-review-filter]");
    if (reviewFilterButton) {
      activeReviewFilter = reviewFilterButton.dataset.reviewFilter;
      document.querySelectorAll("[data-review-filter]").forEach((b) =>
        b.classList.toggle("is-active", b === reviewFilterButton),
      );
      tablePages.reviews.page = 1;
      renderReviews();
      return;
    }

    const userRoleButton = e.target.closest("[data-user-role]");
    if (userRoleButton) {
      activeUserRole = userRoleButton.dataset.userRole;
      document.querySelectorAll("[data-user-role]").forEach((button) => {
        const isActive = button === userRoleButton;
        button.classList.toggle("is-active", isActive);
        button.setAttribute("aria-selected", String(isActive));
      });
      tablePages.users.page = 1;
      renderUsers();
      return;
    }

    const serviceEditButton = e.target.closest("[data-service-edit]");
    if (serviceEditButton) {
      const service = state.services.find((item) => item.id === serviceEditButton.dataset.serviceEdit);
      if (service) {
        fillServiceForm(service);
        document.querySelector("#serviceDialog").showModal();
      }
      return;
    }

    const serviceDeleteButton = e.target.closest("[data-service-delete]");
    if (serviceDeleteButton) {
      if (!window.confirm("Скрыть эту услугу из каталога?")) return;
      try {
        await apiFetch(`/admin/services/${serviceDeleteButton.dataset.serviceDelete}`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Услуга скрыта");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const serviceRestoreButton = e.target.closest("[data-service-restore]");
    if (serviceRestoreButton) {
      try {
        await apiFetch(`/admin/services/${serviceRestoreButton.dataset.serviceRestore}`, {
          method: "PATCH",
          body: JSON.stringify({ isActive: true }),
        });
        await loadAll();
        renderAll();
        showToast("Услуга возвращена в каталог");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const serviceHardDeleteButton = e.target.closest("[data-service-hard-delete]");
    if (serviceHardDeleteButton) {
      if (!window.confirm("Полностью удалить эту услугу из базы? Действие необратимо.")) return;
      try {
        await apiFetch(`/admin/services/${serviceHardDeleteButton.dataset.serviceHardDelete}/hard`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Услуга удалена");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const productEditButton = e.target.closest("[data-product-edit]");
    if (productEditButton) {
      const product = state.products.find((item) => item.id === productEditButton.dataset.productEdit);
      if (product) {
        fillProductForm(product);
        document.querySelector("#productDialog").showModal();
      }
      return;
    }

    const productDeleteButton = e.target.closest("[data-product-delete]");
    if (productDeleteButton) {
      if (!window.confirm("Скрыть этот товар из каталога?")) return;
      try {
        await apiFetch(`/admin/products/${productDeleteButton.dataset.productDelete}`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Товар скрыт");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const productRestoreButton = e.target.closest("[data-product-restore]");
    if (productRestoreButton) {
      try {
        await apiFetch(`/admin/products/${productRestoreButton.dataset.productRestore}`, {
          method: "PATCH",
          body: JSON.stringify({ isActive: true }),
        });
        await loadAll();
        renderAll();
        showToast("Товар возвращён в каталог");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const productHardDeleteButton = e.target.closest("[data-product-hard-delete]");
    if (productHardDeleteButton) {
      if (!window.confirm("Полностью удалить этот товар из базы? Действие необратимо.")) return;
      try {
        await apiFetch(`/admin/products/${productHardDeleteButton.dataset.productHardDelete}/hard`, { method: "DELETE" });
        await loadAll();
        renderAll();
        showToast("Товар удалён");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const toastButton = e.target.closest("[data-toast]");
    if (toastButton) showToast(toastButton.dataset.toast);
  });

  document.querySelector("#logoutBtnNav").addEventListener("click", logout);

  const dialog = document.querySelector("#appointmentDialog");
  document.querySelector("#openAppointmentDialog").addEventListener("click", () => {
    syncAppointmentSelects("service");
    dialog.showModal();
  });
  document.querySelector("#appointmentService").addEventListener("change", () => {
    syncAppointmentSelects("service");
  });
  document.querySelector("#appointmentSpecialist").addEventListener("change", () => {
    syncAppointmentSelects("specialist");
  });

  const specialistDialog = document.querySelector("#specialistDialog");
  document.querySelector("#openSpecialistDialog").addEventListener("click", () => {
    fillSpecialistForm();
    specialistDialog.showModal();
  });
  document.querySelector("#specialistSpecialization").addEventListener("change", (e) => {
    renderSpecialistServiceOptions(e.target.value);
  });

  const scheduleDialog = document.querySelector("#scheduleDialog");
  document.querySelector("#openScheduleDialog").addEventListener("click", () => {
    if (state.specialists.length === 0) {
      showToast("Сначала нужен специалист");
      return;
    }
    fillScheduleForm();
    scheduleDialog.showModal();
  });

  const userDialog = document.querySelector("#userDialog");
  document.querySelector("#openUserDialog").addEventListener("click", () => {
    fillUserForm();
    userDialog.showModal();
  });

  const reviewDialog = document.querySelector("#reviewDialog");
  document.querySelector("#openReviewDialog").addEventListener("click", () => {
    fillReviewForm();
    reviewDialog.showModal();
  });

  const serviceCategoryDialog = document.querySelector("#serviceCategoryDialog");
  document.querySelector("#openServiceCategoryDialog").addEventListener("click", () => {
    fillServiceCategoryForm();
    serviceCategoryDialog.showModal();
  });

  const productCategoryDialog = document.querySelector("#productCategoryDialog");
  document.querySelector("#openProductCategoryDialog").addEventListener("click", () => {
    const form = document.querySelector("#productCategoryForm");
    form.reset();
    form.elements.slug.dataset.userEdited = "";
    productCategoryDialog.showModal();
  });

  wireAutoSlug("#serviceCategoryForm");
  wireAutoSlug("#productCategoryForm");
  wireAutoSlug("#serviceForm");
  wireAutoSlug("#productForm");
  wireAllImagePickers();

  const serviceDialog = document.querySelector("#serviceDialog");
  document.querySelector("#openServiceDialog").addEventListener("click", () => {
    if (state.serviceCategories.length === 0) {
      showToast("Сначала нужны категории услуг");
      return;
    }
    fillServiceForm();
    serviceDialog.showModal();
  });

  const productDialog = document.querySelector("#productDialog");
  document.querySelector("#openProductDialog").addEventListener("click", () => {
    if (state.productCategories.length === 0) {
      showToast("Сначала нужны категории товаров");
      return;
    }
    fillProductForm();
    productDialog.showModal();
  });

  document.querySelector("#exportProducts").addEventListener("click", () => {
    const params = new URLSearchParams();
    if (tablePages.products.search) params.set("search", tablePages.products.search);
    const qs = params.toString();
    downloadExport(`/admin/exports/products.csv${qs ? "?" + qs : ""}`, "products");
  });

  document.querySelector("#exportOrders").addEventListener("click", () => {
    const params = new URLSearchParams();
    if (tablePages.orders.search) params.set("search", tablePages.orders.search);
    const qs = params.toString();
    downloadExport(`/admin/exports/orders.csv${qs ? "?" + qs : ""}`, "orders");
  });

  document.addEventListener("submit", async (e) => {
    const contactForm = e.target.closest("[data-appointment-contact-form]");
    if (contactForm) {
      e.preventDefault();
      const appointmentId = contactForm.dataset.appointmentContactForm;
      const fd = new FormData(contactForm);
      try {
        await apiFetch(`/admin/appointments/${appointmentId}/contact`, {
          method: "PATCH",
          body: JSON.stringify({
            patientContactStatus: fd.get("patientContactStatus"),
            patientContactComment: fd.get("patientContactComment") || null,
          }),
        });
        if (contactForm.closest("#appointmentEditDialog")) {
          document.querySelector("#appointmentEditDialog").close();
        }
        await loadAll();
        renderAll();
        showToast("Результат звонка сохранён");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
      return;
    }

    const rescheduleForm = e.target.closest("[data-appointment-reschedule-form]");
    if (rescheduleForm) {
      e.preventDefault();
      const appointmentId = rescheduleForm.dataset.appointmentRescheduleForm;
      const fd = new FormData(rescheduleForm);
      try {
        await apiFetch(`/admin/appointments/${appointmentId}/reschedule`, {
          method: "PATCH",
          body: JSON.stringify({
            specialistId: fd.get("specialistId"),
            date: fd.get("date"),
            time: fd.get("time"),
            comment: fd.get("comment") || null,
          }),
        });
        if (rescheduleForm.closest("#appointmentEditDialog")) {
          document.querySelector("#appointmentEditDialog").close();
        }
        await loadAll();
        renderAll();
        showToast("Запись перенесена");
      } catch (err) {
        showToast(`Ошибка: ${err.message}`);
      }
    }
  });

  const orderDialog = document.querySelector("#orderDialog");
  document.querySelector("#openOrderDialog").addEventListener("click", () => {
    const hasPatient = state.users.some((u) => u.role === "patient");
    if (!hasPatient) {
      showToast("Нет ни одного покупателя (пациента)");
      return;
    }
    if (state.products.filter((p) => p.isActive).length === 0) {
      showToast("Сначала нужен хотя бы один активный товар");
      return;
    }
    const form = document.querySelector("#orderForm");
    form.reset();
    document.querySelector("#orderItemsContainer").innerHTML = "";
    addOrderItemRow();
    orderDialog.showModal();
  });
  document.querySelector("#orderAddItem").addEventListener("click", addOrderItemRow);
  document.querySelector("#orderUserId").addEventListener("change", (e) => {
    const user = state.users.find((u) => u.id === e.target.value);
    if (!user) return;
    const form = document.querySelector("#orderForm");
    if (!form.elements.recipientName.value) form.elements.recipientName.value = user.fullName;
    if (!form.elements.recipientPhone.value) form.elements.recipientPhone.value = user.phone;
  });

  document.querySelector("#specialistForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const specialistId = form.elements.id.value;
    try {
      await apiFetch(specialistId ? `/admin/specialists/${specialistId}` : "/admin/specialists", {
        method: specialistId ? "PATCH" : "POST",
        body: JSON.stringify(getSpecialistPayload(form)),
      });
      specialistDialog.close();
      await loadAll();
      switchPanel("specialists");
      renderAll();
      showToast(specialistId ? "Врач обновлён" : "Врач успешно добавлен");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#scheduleForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const scheduleId = form.elements.id.value;
    try {
      await apiFetch(scheduleId ? `/admin/doctor-schedule/${scheduleId}` : "/admin/doctor-schedule", {
        method: scheduleId ? "PATCH" : "POST",
        body: JSON.stringify(getSchedulePayload(form)),
      });
      scheduleDialog.close();
      await loadAll();
      switchPanel("specialists");
      renderAll();
      showToast(scheduleId ? "Окно записи обновлено" : "Окно записи добавлено");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#userForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const userId = form.elements.id.value;
    try {
      await apiFetch(userId ? `/admin/users/${userId}` : "/admin/users", {
        method: userId ? "PATCH" : "POST",
        body: JSON.stringify(getUserPayload(form, Boolean(userId))),
      });
      userDialog.close();
      await loadAll();
      switchPanel("users");
      renderAll();
      showToast(userId ? "Пользователь обновлён" : "Пользователь добавлен");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#reviewForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const revId = form.elements.id.value;
    try {
      await apiFetch(revId ? `/admin/reviews/${revId}` : "/admin/reviews", {
        method: revId ? "PATCH" : "POST",
        body: JSON.stringify(getReviewPayload(form)),
      });
      reviewDialog.close();
      await loadAll();
      switchPanel("reviews");
      renderAll();
      showToast(revId ? "Отзыв обновлён" : "Отзыв добавлен");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#serviceForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const serviceId = form.elements.id.value;
    try {
      await apiFetch(serviceId ? `/admin/services/${serviceId}` : "/admin/services", {
        method: serviceId ? "PATCH" : "POST",
        body: JSON.stringify(getServicePayload(form)),
      });
      serviceDialog.close();
      await loadAll();
      switchPanel("services");
      renderAll();
      showToast(serviceId ? "Услуга обновлена" : "Услуга добавлена");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#serviceCategoryForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const categoryId = form.elements.id.value;
    try {
      await apiFetch(
        categoryId ? `/admin/service-categories/${categoryId}` : "/admin/service-categories",
        {
          method: categoryId ? "PATCH" : "POST",
          body: JSON.stringify({
            title: form.elements.title.value.trim(),
            slug: form.elements.slug.value.trim(),
            description: optionalText(form.elements.description.value),
            imageUrl: optionalText(form.elements.imageUrl.value),
          }),
        }
      );
      serviceCategoryDialog.close();
      await loadAll();
      switchPanel("services");
      renderAll();
      showToast(categoryId ? "Категория обновлена" : "Категория добавлена");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#productCategoryForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    try {
      await apiFetch("/admin/product-categories", {
        method: "POST",
        body: JSON.stringify({
          title: form.elements.title.value.trim(),
          slug: form.elements.slug.value.trim(),
        }),
      });
      productCategoryDialog.close();
      await loadAll();
      switchPanel("store");
      renderAll();
      showToast("Категория товаров добавлена");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#productForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const productId = form.elements.id.value;
    try {
      await apiFetch(productId ? `/admin/products/${productId}` : "/admin/products", {
        method: productId ? "PATCH" : "POST",
        body: JSON.stringify(getProductPayload(form)),
      });
      productDialog.close();
      await loadAll();
      switchPanel("store");
      renderAll();
      showToast(productId ? "Товар обновлён" : "Товар добавлен");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#orderForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const form = e.currentTarget;
    const items = [...document.querySelectorAll("#orderItemsContainer .order-item-row")]
      .map((row) => ({
        productId: row.querySelector(".order-item-product").value,
        quantity: Number(row.querySelector(".order-item-qty").value),
      }))
      .filter((item) => item.productId && item.quantity >= 1);
    if (items.length === 0) {
      showToast("Добавьте хотя бы один товар");
      return;
    }
    const payload = {
      userId: form.elements.userId.value,
      items,
      paymentMethod: form.elements.paymentMethod.value,
      deliveryMethod: form.elements.deliveryMethod.value,
      deliveryAddress: form.elements.deliveryAddress.value.trim(),
      recipientName: form.elements.recipientName.value.trim(),
      recipientPhone: form.elements.recipientPhone.value.trim(),
      comment: optionalText(form.elements.comment.value),
    };
    try {
      await apiFetch("/admin/orders", { method: "POST", body: JSON.stringify(payload) });
      orderDialog.close();
      await loadAll();
      switchPanel("orders");
      renderAll();
      showToast("Заказ создан");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });

  document.querySelector("#appointmentForm").addEventListener("submit", async (e) => {
    if (e.submitter?.value === "cancel") return;
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await apiFetch("/appointments", {
        method: "POST",
        body: JSON.stringify({
          serviceId: fd.get("serviceId"),
          specialistId: fd.get("specialistId"),
          date: fd.get("date"),
          time: fd.get("time"),
          patientName: fd.get("patientName"),
          patientPhone: fd.get("patientPhone"),
          comment: fd.get("comment") || null,
        }),
      });
      dialog.close();
      await loadAll();
      switchPanel("appointments");
      renderAll();
      showToast("Новая запись добавлена");
    } catch (err) {
      showToast(`Ошибка: ${err.message}`);
    }
  });
}

function showLoginScreen() {
  document.getElementById("loginScreen").style.display = "flex";
  document.getElementById("adminShell").style.display = "none";
}

function showAdminShell() {
  document.getElementById("loginScreen").style.display = "none";
  document.getElementById("adminShell").style.display = "";
}

async function logout() {
  try {
    await apiFetch("/auth/logout", { method: "POST" });
  } catch (_) {}
  accessToken = null;
  showLoginScreen();
}

function bindLoginForm() {
  const form = document.getElementById("loginForm");
  const errorEl = document.getElementById("loginError");
  const submitBtn = document.getElementById("loginSubmit");
  const passwordInput = document.getElementById("loginPassword");
  const passwordToggle = document.getElementById("toggleLoginPassword");

  passwordToggle?.addEventListener("click", () => {
    const isVisible = passwordInput.type === "text";
    passwordInput.type = isVisible ? "password" : "text";
    passwordToggle.classList.toggle("is-visible", !isVisible);
    passwordToggle.setAttribute("aria-pressed", String(!isVisible));
    passwordToggle.setAttribute("aria-label", isVisible ? "Показать пароль" : "Скрыть пароль");
    passwordInput.focus();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    submitBtn.disabled = true;
    submitBtn.textContent = "Вхожу…";

    const phone = form.phone.value.trim();
    const password = form.password.value;
    const remember = form.remember?.checked ?? true;

    try {
      await login(phone, password, remember);
      await enterAdmin();
    } catch (err) {
      errorEl.textContent = err.message;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Войти";
    }
  });
}

// Поля раздела «Настройки». type: text (по умолчанию) | number | bool | list.
const SETTINGS_FIELDS = [
  { key: "brandName" },
  { key: "panelName" },
  { key: "currencySymbol" },
  { key: "locale" },
  { key: "overviewStartDate" },
  { key: "paginationSizes", type: "list" },
  { key: "clinicPhone" },
  { key: "clinicEmail" },
  { key: "clinicAddress" },
  { key: "clinicHours" },
  { key: "legalName" },
  { key: "bin" },
  { key: "licenseNumber" },
  { key: "licenseFileUrl" },
  { key: "defaultSlotMinutes", type: "number" },
  { key: "bookingHorizonDays", type: "number" },
  { key: "minLeadHours", type: "number" },
  { key: "onlineBookingEnabled", type: "bool" },
  { key: "remindersEnabled", type: "bool" },
  { key: "reminderLeadHours", type: "number" },
];

function populateSettingsForm() {
  const form = document.querySelector("#settingsForm");
  if (!form) return;
  SETTINGS_FIELDS.forEach(({ key, type }) => {
    const input = form.elements[key];
    if (!input) return;
    const value = ADMIN_CONFIG[key];
    if (type === "bool") {
      input.checked = Boolean(value);
    } else if (type === "list") {
      input.value = Array.isArray(value) ? value.join(", ") : value ?? "";
    } else {
      input.value = value ?? "";
    }
  });
  renderLicenseWidget();
}

function renderLicenseWidget() {
  const linkEl = document.getElementById("licenseFileLink");
  const labelEl = document.getElementById("licenseUploadLabel");
  const deleteBtn = document.getElementById("licenseFileDelete");
  if (!linkEl || !labelEl || !deleteBtn) return;
  const url = ADMIN_CONFIG.licenseFileUrl;
  if (url) {
    linkEl.textContent = "Открыть текущий PDF";
    linkEl.href = url;
    linkEl.classList.remove("is-empty");
    labelEl.textContent = "Заменить";
    deleteBtn.disabled = false;
  } else {
    linkEl.textContent = "Файл не загружен";
    linkEl.removeAttribute("href");
    linkEl.classList.add("is-empty");
    labelEl.textContent = "Загрузить";
    deleteBtn.disabled = true;
  }
}

async function uploadLicense(file) {
  if (!file) return;
  if (file.type !== "application/pdf") {
    showToast("Допускаются только PDF-файлы");
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showToast("Файл больше 10 МБ");
    return;
  }
  const fd = new FormData();
  fd.append("file", file);
  try {
    // FormData нельзя гнать через apiFetch — он ставит Content-Type: application/json.
    const res = await fetch(`${API_BASE}/admin/settings/license`, {
      method: "POST",
      credentials: "include",
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
      body: fd,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(typeof body.detail === "string" ? body.detail : res.statusText);
    }
    const data = await res.json();
    applySettings(data && data.settings ? data.settings : {});
    showToast("Файл лицензии загружен");
  } catch (err) {
    showToast(`Ошибка загрузки: ${err.message}`);
  }
}

async function deleteLicense() {
  if (!window.confirm("Удалить файл лицензии?")) return;
  try {
    const resp = await apiFetch("/admin/settings/license", { method: "DELETE" });
    applySettings(resp && resp.settings ? resp.settings : {});
    showToast("Файл лицензии удалён");
  } catch (err) {
    showToast(`Ошибка удаления: ${err.message}`);
  }
}

function bindLicenseUploader() {
  const handleFile = (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    uploadLicense(file);
  };
  document.getElementById("licenseFileInput")?.addEventListener("change", handleFile);
  document.getElementById("licenseFileDelete")?.addEventListener("click", deleteLicense);
}

function readSettingsForm() {
  const form = document.querySelector("#settingsForm");
  const data = {};
  if (!form) return data;
  SETTINGS_FIELDS.forEach(({ key, type }) => {
    const input = form.elements[key];
    if (!input) return;
    if (type === "bool") {
      data[key] = input.checked;
      return;
    }
    const raw = input.value.trim();
    if (type === "list") {
      const sizes = raw
        .split(",")
        .map((n) => Number(n.trim()))
        .filter((n) => Number.isFinite(n) && n > 0);
      if (sizes.length) data[key] = sizes;
    } else if (type === "number") {
      const num = Number(raw);
      if (raw !== "" && Number.isFinite(num)) data[key] = num;
    } else if (raw) {
      data[key] = raw;
    }
  });
  return data;
}

// Применяет переданные значения поверх дефолтов и обновляет интерфейс на лету.
function applySettings(overrides) {
  Object.assign(ADMIN_CONFIG, ADMIN_DEFAULTS, overrides);
  OVERVIEW_START_DATE = new Date(`${ADMIN_CONFIG.overviewStartDate}T00:00:00`);
  applyAdminConfig();
  populateSettingsForm();
  renderAll();
}

// Загружает настройки с сервера и применяет их. Вызывается после входа.
// Ошибка здесь не критична — остаёмся на значениях по умолчанию.
async function loadSettings() {
  try {
    const resp = await apiFetch("/admin/settings");
    applySettings(resp && resp.settings ? resp.settings : {});
  } catch (err) {
    console.warn("Не удалось загрузить настройки:", err.message);
  }
}

async function saveSettings() {
  const data = readSettingsForm();
  try {
    const resp = await apiFetch("/admin/settings", {
      method: "PUT",
      body: JSON.stringify({ settings: data }),
    });
    applySettings(resp && resp.settings ? resp.settings : data);
    showToast("Настройки сохранены");
  } catch (err) {
    showToast(`Ошибка сохранения настроек: ${err.message}`);
  }
}

async function resetSettings() {
  try {
    const resp = await apiFetch("/admin/settings", {
      method: "PUT",
      body: JSON.stringify({ settings: {} }),
    });
    applySettings(resp && resp.settings ? resp.settings : {});
    showToast("Настройки сброшены");
  } catch (err) {
    showToast(`Ошибка сброса настроек: ${err.message}`);
  }
}

function applyAdminConfig() {
  document.title = ADMIN_CONFIG.documentTitle;
  document.documentElement.lang = ADMIN_CONFIG.locale.split("-")[0] || "ru";
  document.querySelectorAll("[data-admin-brand]").forEach((element) => {
    element.textContent = ADMIN_CONFIG.brandName;
  });
  document.querySelectorAll("[data-admin-panel-name]").forEach((element) => {
    element.textContent = ADMIN_CONFIG.panelName;
  });
  document.querySelectorAll("[data-admin-home-link]").forEach((element) => {
    element.href = ADMIN_CONFIG.homeUrl;
  });
  document.querySelectorAll("[data-admin-phone-placeholder]").forEach((element) => {
    element.placeholder = ADMIN_CONFIG.phonePlaceholder;
  });

  // Контакты клиники в боковой панели
  const setText = (selector, value, hideWhenEmpty = true) => {
    document.querySelectorAll(selector).forEach((element) => {
      element.textContent = value || "";
      if (hideWhenEmpty) element.style.display = value ? "" : "none";
    });
  };
  setText("[data-clinic-hours]", ADMIN_CONFIG.clinicHours);
  setText("[data-clinic-address]", ADMIN_CONFIG.clinicAddress);
  document.querySelectorAll("[data-clinic-phone]").forEach((element) => {
    const phone = ADMIN_CONFIG.clinicPhone || "";
    element.textContent = phone;
    element.style.display = phone ? "" : "none";
    if (element.tagName === "A") {
      element.href = phone ? `tel:${phone.replace(/[^\d+]/g, "")}` : "#";
    }
  });
}

applyAdminConfig();
bindLoginForm();
// Если в браузере есть действующая refresh-кука («Запомнить меня») — входим без
// повторного ввода пароля.
tryRestoreSession().then((ok) => {
  if (ok) {
    enterAdmin();
  } else {
    showLoginScreen();
  }
});

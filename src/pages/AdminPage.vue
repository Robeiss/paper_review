<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  createAdminRule,
  createAdminRuleChange,
  createAdminVersion,
  deleteAdminRule,
  deleteAdminRuleChange,
  fetchAdminRuleChanges,
  fetchAdminRules,
  fetchAdminVersions,
  fetchAuditLogs,
  publishAdminVersion,
  saveAdminRule,
  saveAdminRuleChange,
} from '../services/adminService';
import type { AuthSession, RuleChange, RuleVersion, ThesisRule } from '../types/thesis';

const props = defineProps<{
  session: AuthSession;
}>();

defineEmits<{
  logout: [];
}>();

const rules = ref<ThesisRule[]>([]);
const versions = ref<Array<RuleVersion & { status?: string }>>([]);
const ruleChanges = ref<RuleChange[]>([]);
const logs = ref<Array<Record<string, string | number>>>([]);
const activeRuleId = ref('');
const activeChangeId = ref<number | null>(null);
const message = ref('');
const error = ref('');
const loading = ref(false);

const ruleForm = ref<ThesisRule>(emptyRule());
const changeForm = ref<RuleChange>(emptyRuleChange());
const versionForm = ref<RuleVersion & { status: string }>({
  id: '',
  name: '',
  publishedAt: new Date().toISOString().slice(0, 10),
  source: '教务处格式通知',
  status: 'draft',
  changes: [''],
});

const selectedRule = computed(() => rules.value.find((rule) => rule.id === activeRuleId.value));
const selectedChange = computed(() => ruleChanges.value.find((change) => change.id === activeChangeId.value));
const publishedVersion = computed(() => versions.value.find((version) => version.status === 'published') ?? versions.value[0]);

function emptyRule(): ThesisRule {
  return {
    id: '',
    name: '',
    summary: '',
    specs: [{ label: '字体', value: '小四宋体' }],
    notes: [''],
    commonMistakes: [''],
    severity: 'normal',
    updatedAt: new Date().toISOString().slice(0, 10),
  };
}

function emptyRuleChange(): RuleChange {
  return {
    versionId: publishedVersion.value?.id ?? '2026-undergraduate-v1',
    ruleId: rules.value[0]?.id ?? 'rule.body',
    title: '',
    previous: '',
    current: '',
    impact: '',
    risk: 'medium',
  };
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function setRuleForm(rule: ThesisRule) {
  activeRuleId.value = rule.id;
  ruleForm.value = clone(rule);
  if (!ruleForm.value.specs.length) ruleForm.value.specs.push({ label: '', value: '' });
  if (!ruleForm.value.notes.length) ruleForm.value.notes.push('');
  if (!ruleForm.value.commonMistakes.length) ruleForm.value.commonMistakes.push('');
}

function setChangeForm(change: RuleChange) {
  activeChangeId.value = change.id ?? null;
  changeForm.value = clone(change);
}

function newRule() {
  activeRuleId.value = '';
  ruleForm.value = emptyRule();
}

function newRuleChange() {
  activeChangeId.value = null;
  changeForm.value = emptyRuleChange();
}

async function loadAdminData() {
  loading.value = true;
  error.value = '';
  try {
    [rules.value, versions.value, ruleChanges.value, logs.value] = await Promise.all([
      fetchAdminRules(props.session.token),
      fetchAdminVersions(props.session.token),
      fetchAdminRuleChanges(props.session.token),
      fetchAuditLogs(props.session.token),
    ]);
    if (!activeRuleId.value && rules.value[0]) setRuleForm(rules.value[0]);
    if (!activeChangeId.value && ruleChanges.value[0]) setChangeForm(ruleChanges.value[0]);
  } catch (err) {
    error.value = err instanceof Error ? `后台数据加载失败：${err.message}` : '后台数据加载失败';
  } finally {
    loading.value = false;
  }
}

function normalizeRuleForm() {
  ruleForm.value.specs = ruleForm.value.specs.filter((spec) => spec.label.trim() || spec.value.trim());
  ruleForm.value.notes = ruleForm.value.notes.map((note) => note.trim()).filter(Boolean);
  ruleForm.value.commonMistakes = ruleForm.value.commonMistakes.map((mistake) => mistake.trim()).filter(Boolean);
}

function addSpec() {
  ruleForm.value.specs.push({ label: '', value: '' });
}

function removeSpec(index: number) {
  ruleForm.value.specs.splice(index, 1);
  if (!ruleForm.value.specs.length) addSpec();
}

function addNote() {
  ruleForm.value.notes.push('');
}

function removeNote(index: number) {
  ruleForm.value.notes.splice(index, 1);
  if (!ruleForm.value.notes.length) addNote();
}

function addMistake() {
  ruleForm.value.commonMistakes.push('');
}

function removeMistake(index: number) {
  ruleForm.value.commonMistakes.splice(index, 1);
  if (!ruleForm.value.commonMistakes.length) addMistake();
}

function addVersionChange() {
  versionForm.value.changes.push('');
}

function removeVersionChange(index: number) {
  versionForm.value.changes.splice(index, 1);
  if (!versionForm.value.changes.length) addVersionChange();
}

async function saveRuleForm() {
  message.value = '';
  error.value = '';
  try {
    normalizeRuleForm();
    if (selectedRule.value) {
      await saveAdminRule(props.session.token, ruleForm.value);
      message.value = '规则已保存';
    } else {
      await createAdminRule(props.session.token, ruleForm.value);
      message.value = '规则已创建';
    }
    await loadAdminData();
    setRuleForm(ruleForm.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败';
  }
}

async function removeRule() {
  if (!selectedRule.value) return;
  message.value = '';
  error.value = '';
  try {
    await deleteAdminRule(props.session.token, selectedRule.value.id);
    message.value = '规则已删除';
    activeRuleId.value = '';
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败';
  }
}

async function saveChangeForm() {
  message.value = '';
  error.value = '';
  try {
    if (selectedChange.value && changeForm.value.id) {
      await saveAdminRuleChange(props.session.token, changeForm.value);
      message.value = '变更项已保存';
    } else {
      await createAdminRuleChange(props.session.token, changeForm.value);
      message.value = '变更项已创建';
    }
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存变更项失败';
  }
}

async function removeChange() {
  if (!selectedChange.value?.id) return;
  message.value = '';
  error.value = '';
  try {
    await deleteAdminRuleChange(props.session.token, selectedChange.value.id);
    message.value = '变更项已删除';
    activeChangeId.value = null;
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除变更项失败';
  }
}

async function createVersion() {
  message.value = '';
  error.value = '';
  try {
    versionForm.value.changes = versionForm.value.changes.map((change) => change.trim()).filter(Boolean);
    await createAdminVersion(props.session.token, versionForm.value);
    message.value = '版本草稿已创建';
    versionForm.value.changes = [''];
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建版本失败';
  }
}

async function publishVersion(versionId: string) {
  message.value = '';
  error.value = '';
  try {
    await publishAdminVersion(props.session.token, versionId);
    message.value = '版本已发布';
    await loadAdminData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发布失败';
  }
}

onMounted(loadAdminData);
</script>

<template>
  <main class="admin-shell">
    <header class="admin-topbar">
      <div>
        <h1>后台管理</h1>
        <p>{{ session.user.name }} · {{ session.user.account }}</p>
      </div>
      <button type="button" @click="$emit('logout')">退出</button>
    </header>

    <section class="admin-grid">
      <p v-if="loading" class="admin-loading">后台数据加载中...</p>
      <aside class="admin-list">
        <div class="admin-section-title">
          <h2>规则</h2>
          <button type="button" @click="newRule">新增</button>
        </div>
        <button
          v-for="rule in rules"
          :key="rule.id"
          type="button"
          class="admin-rule-item"
          :class="{ active: rule.id === activeRuleId }"
          @click="setRuleForm(rule)"
        >
          <strong>{{ rule.name }}</strong>
          <span>{{ rule.id }}</span>
        </button>
      </aside>

      <section class="admin-editor">
        <div class="admin-section-title">
          <h2>{{ selectedRule ? '编辑规则' : '新增规则' }}</h2>
          <div class="admin-actions">
            <button type="button" @click="saveRuleForm">保存</button>
            <button type="button" class="danger" :disabled="!selectedRule" @click="removeRule">删除</button>
          </div>
        </div>

        <p v-if="message" class="admin-message">{{ message }}</p>
        <p v-if="error" class="admin-error">{{ error }}</p>

        <div class="form-grid">
          <label>
            <span>规则 ID</span>
            <input v-model="ruleForm.id" :disabled="Boolean(selectedRule)" />
          </label>
          <label>
            <span>名称</span>
            <input v-model="ruleForm.name" />
          </label>
          <label>
            <span>级别</span>
            <select v-model="ruleForm.severity">
              <option value="normal">常规</option>
              <option value="important">关注</option>
              <option value="critical">重点</option>
            </select>
          </label>
          <label>
            <span>更新日期</span>
            <input v-model="ruleForm.updatedAt" />
          </label>
        </div>

        <label class="wide-field">
          <span>摘要</span>
          <textarea v-model="ruleForm.summary" rows="3"></textarea>
        </label>

        <section class="admin-form-section">
          <div class="admin-section-title compact">
            <h3>格式项</h3>
            <button type="button" @click="addSpec">添加格式项</button>
          </div>
          <div class="editable-list">
            <div v-for="(spec, index) in ruleForm.specs" :key="index" class="editable-row two-columns">
              <input v-model="spec.label" placeholder="项目，例如：字体" />
              <input v-model="spec.value" placeholder="要求，例如：小四宋体" />
              <button type="button" class="ghost danger-text" @click="removeSpec(index)">删除</button>
            </div>
          </div>
        </section>

        <section class="admin-form-section">
          <div class="admin-section-title compact">
            <h3>要求说明</h3>
            <button type="button" @click="addNote">添加说明</button>
          </div>
          <div class="editable-list">
            <div v-for="(_, index) in ruleForm.notes" :key="index" class="editable-row one-column">
              <input v-model="ruleForm.notes[index]" placeholder="输入一条要求说明" />
              <button type="button" class="ghost danger-text" @click="removeNote(index)">删除</button>
            </div>
          </div>
        </section>

        <section class="admin-form-section">
          <div class="admin-section-title compact">
            <h3>常见错误</h3>
            <button type="button" @click="addMistake">添加错误</button>
          </div>
          <div class="editable-list">
            <div v-for="(_, index) in ruleForm.commonMistakes" :key="index" class="editable-row one-column">
              <input v-model="ruleForm.commonMistakes[index]" placeholder="输入一条常见错误" />
              <button type="button" class="ghost danger-text" @click="removeMistake(index)">删除</button>
            </div>
          </div>
        </section>
      </section>

      <aside class="admin-side">
        <section class="admin-card">
          <div class="admin-section-title">
            <h2>规则变更项</h2>
            <button type="button" @click="newRuleChange">新增</button>
          </div>

          <div class="change-admin-list">
            <button
              v-for="change in ruleChanges"
              :key="change.id"
              type="button"
              class="change-admin-item"
              :class="{ active: change.id === activeChangeId }"
              @click="setChangeForm(change)"
            >
              <strong>{{ change.title }}</strong>
              <span>{{ change.ruleId }} · {{ change.risk }}</span>
            </button>
          </div>

          <label>
            <span>所属版本</span>
            <select v-model="changeForm.versionId">
              <option v-for="version in versions" :key="version.id" :value="version.id">{{ version.name }}</option>
            </select>
          </label>
          <label>
            <span>关联规则</span>
            <select v-model="changeForm.ruleId">
              <option v-for="rule in rules" :key="rule.id" :value="rule.id">{{ rule.name }}</option>
            </select>
          </label>
          <label>
            <span>标题</span>
            <input v-model="changeForm.title" />
          </label>
          <label>
            <span>风险等级</span>
            <select v-model="changeForm.risk">
              <option value="low">低风险</option>
              <option value="medium">中风险</option>
              <option value="high">高风险</option>
            </select>
          </label>
          <label>
            <span>上一版要求</span>
            <textarea v-model="changeForm.previous" rows="3"></textarea>
          </label>
          <label>
            <span>当前版要求</span>
            <textarea v-model="changeForm.current" rows="3"></textarea>
          </label>
          <label>
            <span>影响说明</span>
            <textarea v-model="changeForm.impact" rows="3"></textarea>
          </label>
          <div class="admin-actions">
            <button type="button" @click="saveChangeForm">保存变更项</button>
            <button type="button" class="danger" :disabled="!selectedChange" @click="removeChange">删除</button>
          </div>
        </section>

        <section class="admin-card">
          <h2>版本发布</h2>
          <label>
            <span>版本 ID</span>
            <input v-model="versionForm.id" placeholder="2026-undergraduate-v2" />
          </label>
          <label>
            <span>版本名称</span>
            <input v-model="versionForm.name" />
          </label>
          <label>
            <span>发布日期</span>
            <input v-model="versionForm.publishedAt" />
          </label>
          <label>
            <span>来源</span>
            <input v-model="versionForm.source" />
          </label>

          <section class="admin-form-section compact-panel">
            <div class="admin-section-title compact">
              <h3>变更说明</h3>
              <button type="button" @click="addVersionChange">添加</button>
            </div>
            <div class="editable-list">
              <div v-for="(_, index) in versionForm.changes" :key="index" class="editable-row one-column">
                <input v-model="versionForm.changes[index]" placeholder="输入一条版本变化" />
                <button type="button" class="ghost danger-text" @click="removeVersionChange(index)">删除</button>
              </div>
            </div>
          </section>

          <button type="button" @click="createVersion">创建草稿</button>

          <div class="version-list">
            <div v-for="version in versions" :key="version.id" class="version-row">
              <div>
                <strong>{{ version.name }}</strong>
                <span>{{ version.status }} · {{ version.publishedAt }}</span>
              </div>
              <button v-if="version.status !== 'published'" type="button" @click="publishVersion(version.id)">发布</button>
            </div>
          </div>
        </section>

        <section class="admin-card">
          <h2>更新日志</h2>
          <div class="audit-list">
            <div v-for="log in logs" :key="log.id" class="audit-row">
              <strong>{{ log.action }}</strong>
              <span>{{ log.actor }} · {{ log.target }}</span>
              <small>{{ log.created_at }}</small>
            </div>
          </div>
        </section>
      </aside>
    </section>
  </main>
</template>

/**
 * useStepForm - 步骤向导表单逻辑
 *
 * 提供三步骤导航表单的通用逻辑：
 * - 步骤管理（当前步骤、总数）
 * - 步骤导航（上一步、下一步、跳转到指定步骤）
 * - 进度百分比计算
 *
 * 支持外部传入的「可访问步骤集合」与「步骤切换守卫」：
 * - reachableSteps: 当前可自由切换的步骤索引 Set（如 [1, 2, 3] 表示都可点）
 * - 跳转到更远的步骤时,中间步骤必须全部在 reachableSteps 中
 */
import { ref, computed } from 'vue'

export function useStepForm(total = 3) {
  const currentStep = ref(1)
  const totalSteps = total

  // 计算属性
  const isFirstStep = computed(() => currentStep.value === 1)
  const isLastStep = computed(() => currentStep.value === totalSteps)
  const progressPercent = computed(() => (currentStep.value / totalSteps) * 100)

  // 步骤定义
  const steps = [
    { index: 1, title: '核心信息', desc: '手办与金额' },
    { index: 2, title: '店铺与支付', desc: '店铺与定金' },
    { index: 3, title: '物流与备注', desc: '物流与尾款' }
  ]

  /**
   * 判断目标步骤是否可访问
   * @param {number} target - 目标步骤
   * @param {Set<number>|Array<number>} reachableSteps - 可自由切换的步骤集合
   * @returns {boolean}
   */
  function canJumpTo(target, reachableSteps) {
    if (target < 1 || target > totalSteps) return false
    if (target === currentStep.value) return true
    // 向后跳（跳到当前步骤+1 之内）允许
    if (target > currentStep.value && target <= currentStep.value + 1) return true
    // 向前跳总是允许
    if (target < currentStep.value) return true
    // 跳到更远的目标:要求 [currentStep+1, target] 区间内所有步骤都已 accessible
    const reachable = reachableSteps instanceof Set ? reachableSteps : new Set(reachableSteps || [])
    for (let i = currentStep.value + 1; i <= target; i++) {
      if (!reachable.has(i)) return false
    }
    return true
  }

  /**
   * 跳转到指定步骤
   * @param {number} step - 目标步骤
   * @param {Set<number>|Array<number>} reachableSteps - 可自由切换的步骤集合
   */
  function goToStep(step, reachableSteps) {
    if (!canJumpTo(step, reachableSteps)) return false
    currentStep.value = step
    return true
  }

  function nextStep() {
    if (currentStep.value < totalSteps) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  function resetStep() {
    currentStep.value = 1
  }

  return {
    currentStep,
    totalSteps,
    steps,
    isFirstStep,
    isLastStep,
    progressPercent,
    canJumpTo,
    goToStep,
    nextStep,
    prevStep,
    resetStep
  }
}

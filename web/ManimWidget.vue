<template>
  <div class="manim-widget">
    <textarea 
      v-model="code" 
      class="code-editor" 
      placeholder="Enter Manim script here..."
      @input="onCodeChange"
    ></textarea>
  </div>
</template>

<script>
export default {
  name: 'ManimWidget',
  props: {
    value: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      code: this.value || ''
    };
  },
  methods: {
    onCodeChange(event) {
      this.code = event.target.value;
      this.$emit('input', this.code);
    }
  },
  watch: {
    value(newVal) {
      if (newVal !== this.code) {
        this.code = newVal;
      }
    }
  }
};
</script>

<style scoped>
.manim-widget {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.code-editor {
  width: 100%;
  height: 300px;
  background-color: #1e1e1e;
  color: #dcdcdc;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  border: 1px solid #333;
  padding: 10px;
  box-sizing: border-box;
  resize: vertical;
  outline: none;
}

.code-editor:focus {
  border-color: #555;
}
</style>

